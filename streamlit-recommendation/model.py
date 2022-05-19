from scipy.sparse import csr_matrix
import numpy as np
from numba import jit

from sklearn.preprocessing import LabelEncoder


class EASE:
    def __init__(self, df):
        self.df = df
        self.user_enc = LabelEncoder()
        self.item_enc = LabelEncoder()
        self.user2id = dict()
        self.item2id = dict()
        self.id2user = dict()
        self.id2item = dict()

    def _get_users_and_items(self):
        self.users = self.df['user'].unique()
        self.items = self.df['item'].unique()
        n_users = len(self.users)
        n_items = len(self.items)

        self.user2id = dict((uid, i) for i, uid in enumerate(self.users))
        self.item2id = dict((iid, i) for i, iid in enumerate(self.items))
        self.id2user = dict(zip(self.user2id.values(), self.user2id.keys()))
        self.id2item = dict(zip(self.item2id.values(), self.item2id.keys()))

        users = np.array([self.user2id[user] for user in self.df['user']])
        items = np.array([self.item2id[item] for item in self.df['item']])

        return users, items

    def fit(self, lambda_=0.5):
        users, items = self._get_users_and_items()
        values = np.ones(self.df.shape[0])
        print(users.shape, items.shape, values.shape)

        X = csr_matrix((values, (users, items)))
        self.X = X

        G = X.T.dot(X).toarray()
        diagIndices = np.diag_indices(G.shape[0])
        G[diagIndices] += lambda_
        P = np.linalg.inv(G)
        B = P / (-np.diag(P))
        B[diagIndices] = 0

        self.B = B
        self.pred = X.dot(B)
