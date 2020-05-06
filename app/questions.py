from copy import deepcopy

og_qns = {
    "Fill in the blank: 423 x 1000 = ____ x 10": ["42300", "423", "4230", "423000"],
    "Which of the following is closest to 1?": ["4/5", "1/2", "2/3", "3/4" ],
    "Which of the following is the same as 2010 g?": ["2 kg 10 g", "2 kg 1 g", "20 kg 1 g", "20 kg 10 g"],
    "Find the value of (3y +1) / 4 , when y = 5": ["4","9","8","5"],
    "The ratio of Rachel's age to Samy's age is 7 : 6./n \
    Rachel is 4 years older than Samy./n \
    What is Samy's age this year?": ["24", "10","11","28"],
    "How many fifths are there in 2 3/5?": ["13","11","3","6"],
    "The sum of 1/2 and 2/5 is the same as ___.":["0.900", "0.009","0.090", "9.000"],
    "What is the value of 36 + 24 / (9 - 3) + 2 x 5 ?" : ["50","51","60","66"],
    "Sally has 100 marbles and her brother has 300 marbles./n \
    Express Sally's marbles as a percentage of the total number of marbles they have altogether." : ["25%","33 1/3 %","300%","400%"],
    "Mr Tan has an equal number of pens and pencils. He puts the pens in bundles of 8 and the pencils in bundles of 12. \
    There are 15 bundles altogether. How many pens are there?": ["72","24","48","96"],
    "3 ones, 4 tenths and 7 thousandths is ___":["3.407","3.470","3.047","3.740"],
    "Which of the following is equal to 0.25%?" : ["1/400","1/25","1/4","25"]

}

qns = deepcopy(og_qns)
