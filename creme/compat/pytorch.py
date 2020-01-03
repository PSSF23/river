import torch

from .. import base


__all__ = [
    'PyTorch2CremeRegressor'
]


class PyTorch2CremeBase:

    def __init__(self, net, loss_fn, optimizer, batch_size, x_tensor, y_tensor):
        self.net = net
        self.loss_fn = loss_fn
        self.optimizer = optimizer
        self.batch_size = batch_size
        self.x_tensor = x_tensor
        self.y_tensor = y_tensor
        self._x_batch = [None] * batch_size
        self._y_batch = [None] * batch_size
        self._batch_i = 0

    def fit_one(self, x, y):

        self._x_batch[self._batch_i] = list(x.values())
        self._y_batch[self._batch_i] = [y]

        self._batch_i += 1

        if self._batch_i == self.batch_size:

            x = self.x_tensor(self._x_batch)
            y = self.y_tensor(self._y_batch)

            self.optimizer.zero_grad()
            y_pred = self.net(x)
            loss = self.loss_fn(y_pred, y)
            loss.backward()
            self.optimizer.step()
            self._batch_i = 0

        return self


class PyTorch2CremeRegressor(PyTorch2CremeBase, base.Regressor):
    """PyTorck to ``creme`` regressor adapter.

    Parameters:
        net (torch.nn.Sequential)
        loss_fn (torch.nn.modules.loss._Loss)
        optimizer (torch.optim.Optimizer)
        batch_size (int)

    Example:

        ::

            >>> from creme import compat
            >>> from creme import datasets
            >>> from creme import metrics
            >>> from creme import model_selection
            >>> from creme import preprocessing
            >>> import torch
            >>> from torch import nn
            >>> from torch import optim

            >>> _ = torch.manual_seed(0)

            >>> X_y = datasets.TrumpApproval()

            >>> n_features = 6
            >>> net = nn.Sequential(
            ...     nn.Linear(n_features, 3),
            ...     nn.Linear(3, 1)
            ... )

            >>> model = (
            ...     preprocessing.StandardScaler() |
            ...     compat.PyTorch2CremeRegressor(
            ...         net=net,
            ...         loss_fn=nn.MSELoss(),
            ...         optimizer=optim.SGD(net.parameters(), lr=1e-3),
            ...         batch_size=2
            ...     )
            ... )
            >>> metric = metrics.MAE()

            >>> model_selection.progressive_val_score(X_y, model, metric)
            MAE: 2.805633

    """

    def __init__(self, net, loss_fn, optimizer, batch_size=1):
        super().__init__(
            net=net,
            loss_fn=loss_fn,
            optimizer=optimizer,
            batch_size=batch_size,
            x_tensor=torch.FloatTensor,
            y_tensor=torch.FloatTensor
        )

    def predict_one(self, x):
        x = self.x_tensor(list(x.values()))
        return self.net(x).item()
