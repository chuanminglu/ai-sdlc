import tensorflow as tf

# TensorFlow 2.x uses eager execution by default
# This means operations are executed immediately
m1 = tf.constant([3, 5])
m2 = tf.constant([2, 4])

result = tf.add(m1, m2)

# No session needed in TensorFlow 2.x
print(result.numpy())  # Convert tensor to numpy array for display
