import tensorflow as tf

class Model(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, units):
        super(Model, self).__init__()
        self.units = units
        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
        self.gru = tf.keras.layers.GRU(
            self.units,
            return_sequences=True,
            recurrent_activation="sigmoid",
            recurrent_initializer='glorot_uniform',
            stateful=True
        )
        self.fc = tf.keras.layers.Dense(vocab_size)
    def call(self, x):
        embedding = self.embedding(x)
        output = self.gru(embedding)
        prediction = self.fc(output)
        return prediction

