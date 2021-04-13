##### Anthony Lyristis - P-Set 5, Traffic

In order to complete this PSet, I first researched different strategies for constructing a CNN. 
A common approach is to perform max-pooling on each hidden layer's output. Due to this approach we can
increase the number of filters applied in subsequent hidden layers with a more  abstract representation of the dataset. 
I also decided against using Vgg16 so that I could strengthen my own knowledge of the topic.

32 initially random filters was an arbitrary choice, as was the convo kernel of 3x3 for generating each
dot-product from our weights and inputs. Increasing the number of filters as the hidden layers progressed was not an 
arbitrary choice though. According to my research this is a preferred method for improving your model's accuracy.
Max-Pooling each output was also recommended but also seemed obvious after I began to understand the inner workings of the network. 
Without pooling, computation was slightly faster, but slightly less accurate. Adding pooling with a stride > 1 improved speed when pooling but 
reduced accuracy very slightly. Pooling with stride == 1 was my final submission because it generated the highest
accuracy. The output layer is flattened before being passed to the output layer which applies the softmax
activation function to format the final output as a probability distribution.

##### General Observations
- Removing max-pooling greatly increased the training duration but improved accuracy.
- Max-pooling with a stride of every other pixel (2) improved performance but reduced accuracy
- Max-pooling with a stride of 1 took the longest to train but had the highest accuracy