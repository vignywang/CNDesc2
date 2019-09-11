#
# Created by ZhangYuyang on 2019/8/12
#
import torch
import torch.nn as nn
from torch.autograd import Function

# from torchvision.models import ResNet


class Hash(Function):

    @staticmethod
    def forward(ctx, input):
        return torch.sign(input)

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output


def hash_layer(input):
    return Hash.apply(input)


class BasicSuperPointNet(nn.Module):

    def __init__(self):
        super(BasicSuperPointNet, self).__init__()
        self.relu = torch.nn.ReLU(inplace=True)
        self.pool = torch.nn.MaxPool2d(kernel_size=2, stride=2)
        c1, c2, c3, c4, c5, d1 = 64, 64, 128, 128, 256, 256
        # Shared Encoder.
        self.conv1a = nn.Conv2d(1, c1, kernel_size=3, stride=1, padding=1)
        self.conv1b = nn.Conv2d(c1, c1, kernel_size=3, stride=1, padding=1)
        self.conv2a = nn.Conv2d(c1, c2, kernel_size=3, stride=1, padding=1)
        self.conv2b = nn.Conv2d(c2, c2, kernel_size=3, stride=1, padding=1)
        self.conv3a = nn.Conv2d(c2, c3, kernel_size=3, stride=1, padding=1)
        self.conv3b = nn.Conv2d(c3, c3, kernel_size=3, stride=1, padding=1)
        self.conv4a = nn.Conv2d(c3, c4, kernel_size=3, stride=1, padding=1)
        self.conv4b = nn.Conv2d(c4, c4, kernel_size=3, stride=1, padding=1)
        # Detector Head.
        self.convPa = nn.Conv2d(c4, c5, kernel_size=3, stride=1, padding=1)
        self.convPb = nn.Conv2d(c5, 65, kernel_size=1, stride=1, padding=0)
        # Descriptor Head.
        self.convDa = nn.Conv2d(c4, c5, kernel_size=3, stride=1, padding=1)
        self.convDb = nn.Conv2d(c5, d1, kernel_size=1, stride=1, padding=0)

        self.softmax = nn.Softmax(dim=1)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')

    def _encoder(self, x):
        x = self.relu(self.conv1a(x))
        x = self.relu(self.conv1b(x))
        x = self.pool(x)
        x = self.relu(self.conv2a(x))
        x = self.relu(self.conv2b(x))
        x = self.pool(x)
        x = self.relu(self.conv3a(x))
        x = self.relu(self.conv3b(x))
        x = self.pool(x)
        x = self.relu(self.conv4a(x))
        x = self.relu(self.conv4b(x))

        return x

    def _detector_head(self, x):
        cPa = self.relu(self.convPa(x))
        logit = self.convPb(cPa)
        prob = self.softmax(logit)[:, :-1, :, :]

        return logit, prob

    def _descriptor_head(self, x):
        cDa = self.relu(self.convDa(x))
        feature = self.convDb(cDa)

        return feature


class MagicPointNet(BasicSuperPointNet):

    def __init__(self):
        super(MagicPointNet, self).__init__()

    def forward(self, x):
        x = self._encoder(x)
        logit, prob = self._detector_head(x)
        return logit, prob


class SuperPointNet(BasicSuperPointNet):

    def __init__(self, output_type='float', loss_type='triplet'):
        super(SuperPointNet, self).__init__()
        if output_type == 'float':
            self._forward = self._forward_float_triplet
        elif output_type == 'binary':
            if loss_type == 'triplet':
                self._forward = self._forward_float_triplet  # same as output_type='float'
            elif loss_type == 'pairwise':
                self._forward = self._forward_binary_pairwise_direct
            else:
                assert False
        else:
            assert False

    def _forward_float_triplet(self, x):
        x = self._encoder(x)
        logit, prob = self._detector_head(x)

        feature = self._descriptor_head(x)
        dn = torch.norm(feature, p=2, dim=1, keepdim=True)
        desc = feature.div(dn)

        return logit, desc, prob, feature

    def _forward_binary_pairwise_direct(self, x):
        x = self._encoder(x)
        logit, prob = self._detector_head(x)

        feature = self._descriptor_head(x)
        dn = torch.norm(feature, p=2, dim=1, keepdim=True)
        feature = feature.div(dn)
        desc = hash_layer(feature)

        return logit, desc, prob, feature

    def forward(self, x):
        return self._forward(x)


if __name__ == "__main__":
    random_input = torch.randn((1, 1, 240, 320))
    model = SuperPointNet()
    result = model(random_input)








