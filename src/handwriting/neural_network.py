import numpy as np


class NeuralNetwork:
    def __init__(self, input_nodes, hidden_nodes, output_nodes, learning_rate):
        param_size = (input_nodes + 1) * hidden_nodes + (hidden_nodes + 1) * output_nodes
        parameters = (np.random.random(size=param_size) - 0.5) * 0.25

        self.input_nodes = input_nodes
        self.hidden_nodes = hidden_nodes
        self.output_nodes = output_nodes
        self.learning_rate = learning_rate

        self.theta1 = np.matrix(np.reshape(
            parameters[:hidden_nodes*(input_nodes+1)],
            (hidden_nodes, input_nodes+1))
        )

        self.theta2 = np.matrix(np.reshape(
            parameters[hidden_nodes*(input_nodes+1):],
            (output_nodes, hidden_nodes+1))
        )

    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def sigmoid_gradient(self, z):
        return np.multiply(self.sigmoid(z), (1 - self.sigmoid(z)))

    def forward_propagate(self, X):
        m = X.shape[0]
        a1 = np.insert(X, 0, values=np.ones(m), axis=1)
        z2 = a1 * self.theta1.T
        a2 = np.insert(self.sigmoid(z2), 0, values=np.ones(m), axis=1)
        z3 = a2 * self.theta2.T
        h = self.sigmoid(z3)
        return a1, z2, a2, z3, h

    def backward_propagate(self, X, y):
        m = X.shape[0]
        X = np.matrix(X)
        y = np.matrix(y)
        a1, z2, a2, z3, h = self.forward_propagate(X)
        J = 0
        delta1 = np.zeros(self.theta1.shape)
        delta2 = np.zeros(self.theta2.shape)

        for i in range(m):
            first = np.multiply(-y[i, :], np.log(h[i, :]))
            second = np.multiply((1 - y[i, :]), np.log(1 - h[i, :]))
            J += np.sum(first-second)

        J = J / m
        J += self.learning_rate / (2 * m) * (np.sum(np.power(self.theta1[:, 1:], 2)) + np.sum(np.power(self.theta2[:, 1:], 2)))

        for t in range(m):
            a1t = a1[t, :]
            z2t = z2[t, :]
            a2t = a2[t, :]
            ht = h[t, :]
            yt = y[t, :]
            d3t = ht - yt
            z2t = np.insert(z2t, 0, values=np.ones(1))
            d2t = np.multiply((self.theta2.T * d3t.T).T,
                              self.sigmoid_gradient(z2t))
            delta1 = delta1 + (d2t[:, 1:]).T * a1t
            delta2 = delta2 + d3t.T * a2t

        delta1 = delta1 / m
        delta2 = delta2 / m
        delta1[:, 1:] = delta1[:, 1:] + (self.theta1[:, 1:] * self.learning_rate) / m
        delta2[:, 1:] = delta2[:, 1:] + (self.theta2[:, 1:] * self.learning_rate) / m

        grad = np.concatenate((np.ravel(delta1), np.ravel(delta2)))

        return J, grad

    def predict(self, X):
        _, _, _, _, h = self.forward_propagate(np.matrix(X))
        return h

    def predict_values(self, X):
        h = self.predict(X)
        p = (np.argmax(h, axis=1).reshape(1, len(h)))
        return p

    def train(self, X, y, X_test=None, y_test=None, learning_rate_decay=0.9, iterations=100, batch_size=50, verbose=False):
        J_history = []
        train_acc_history = []
        test_acc_history = []

        for i in range(iterations):
            indexes = np.random.choice(X.shape[0], batch_size, replace=True)
            X_batch = X[indexes]
            y_batch = y[indexes]
            y_batch_values = np.argmax(y_batch, axis=1).reshape(1, len(y_batch))

            J, grad = self.backward_propagate(X_batch, y_batch)
            J_history.append(J)

            self.theta1 -= self.learning_rate * np.matrix(np.reshape(
                grad[:self.hidden_nodes*(self.input_nodes+1)],
                (self.hidden_nodes, self.input_nodes+1)))

            self.theta2 -= self.learning_rate * np.matrix(np.reshape(
                grad[self.hidden_nodes*(self.input_nodes+1):],
                (self.output_nodes, self.hidden_nodes+1)))

            if i % batch_size == 0:
                train_acc_history.append((self.predict_values(X_batch) == y_batch_values).mean())

                if X_test is not None and y_test is not None:
                    y_test_values = np.argmax(y_test, axis=1).reshape(1, len(y_test))
                    predicted_test_values = self.predict_values(X_test)
                    test_acc_history.append((predicted_test_values == y_test_values).mean())

                self.learning_rate *= learning_rate_decay

                if verbose:
                    print('i: {: 4d} J: {: 6.4f} train acc.: {: 6.4f} test acc.: {: 6.4f} learn rate: {: 6.5f}'.format(i, J, train_acc_history[-1], test_acc_history[-1], self.learning_rate))

        result = {
            'J_history': J_history,
            'train_acc_history': train_acc_history,
            'test_acc_history': test_acc_history,
        }
        self.training_history = result

        return result
