1. I used a java program to produce ten random strings as the inputs,the length range is [10,100] with increments of 10.
2. I added somelines into the original code(arc.py) as a test code named Testarc.py, when I run this test program, I can get
   running time usages of the encoding and decoing ,and the memory usages of the encoding and decoing
3. For each string with particular length, I excuted the same test program by using the same input.txt for 10 times, and stored
   the output values into an excel document and then calculated the average running time usages and average memory usages.
   Concrete details are in the excel document.
4. I also uploaded some run time pictures, since the test command is a little different since I have to test the memory usages:
   concrete details is in the run time pictures(please follow the first command line if you want test it).\
5. I bulid a fold named String Tests to store the input documents and every encode.txt and decode.txt, by comparing with them, 
   we can make sure that the code is correct.(The original input document is the same as decode.txt after excuting the Arithmetic code)
6. I also ploted four figures, and find that:
   a.The Time complexity of the encode function is O(n);
   b.The Time complexity of the encode function is O(n2);     // I think maybe we can simplify our code for this part, since I can't test a long string because of 
														      // the running time is too long, for a string with length of 100, the average running time is close to two minutes.
   c.The Space complexity of the encode function is O(1);
   d.The Space complexity of the encode function is O(n2);    // Actually the change of memory is pretty small, I think it should be S(n) by observation
														      // Maybe I should not use the excel to plot it,since it says the S(n) is O(n square).
															  // I need your help for this part.
   
