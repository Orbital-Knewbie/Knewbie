



function buildQuiz() {
    // variable to store the HTML output
    const output = [];

    myQuestions.forEach(
        (currentQuestion, questionNumber) => {

            // variable to store the list of possible answers
            const answers = [];

            // and for each available answer...
            for (letter in currentQuestion.answers) {

                // ...add an HTML radio button
                answers.push(
                    `<label>
					<input type="radio" name="question${questionNumber}" value="${letter}"> ${currentQuestion.answers[letter]} </br>
					</label>`
                );
            }

            // add this question and its answers to the output
            output.push(
				`<div class="question"> ${questionNumber+1}. ${currentQuestion.question} </div>
				<div class="answers"> ${answers.join('')} </div></br>`
            );
        }
    );

    // finally combine our output list into one string of HTML and put it on the page
    quizContainer.innerHTML = output.join('');
}


function showResults() {

	// gather answer containers from our quiz
	const answerContainers = quizContainer.querySelectorAll('.answers');

	// keep track of user's answers
	let numCorrect = 0;

	// keep track of questions right and wrong
	var answerQns = { Easy: [0, 0], Med: [0, 0], Hard: [0, 0] }

	// for each question...
	myQuestions.forEach((currentQuestion, questionNumber) => {

		// find selected answer
		const answerContainer = answerContainers[questionNumber];
		const selector = `input[name=question${questionNumber}]:checked`;
		const userAnswer = (answerContainer.querySelector(selector) || {}).value;

		const diff = currentQuestion.difficulty;

		// if answer is correct
		if (userAnswer === currentQuestion.correctAnswer) {
			// add to the number of correct answers
			numCorrect++;
			if (diff === "Easy")
				answerQns.Easy[1]++;
			else
				answerQns.Hard[1]++;
			// color the answers green
			answerContainers[questionNumber].style.color = 'lightgreen';
		}
		// if answer is wrong or blank
		else {
			// color the answers red
			answerContainers[questionNumber].style.color = 'red';
			if (diff === "Easy")
				answerQns.Easy[0]++;
			else
				answerQns.Hard[0]++;
		}
	});
	
	// show number of correct answers out of total
	resultsContainer.innerHTML = `${numCorrect} out of ${myQuestions.length}`;

	
}



// Variables
const quizContainer = document.getElementById('quiz');
const resultsContainer = document.getElementById('results');
const submitButton = document.getElementById('submit');
const myQuestions = [
	{
		question: "Fill in the blank: 423 x 1000 = ____ x 10",
		answers: {
			1: "42300",
			2: "423",
			3: "4230",
			4: "423000"
		},
		correctAnswer: "1",
		difficulty: "Easy"
	},
	{
		question: "Which of the following is closest to 1?",
		answers: {
			1: "4/5",
			2: "1/2",
			3: "2/3",
			4: "3/4"
		},
		correctAnswer: "1",
		difficulty: "Easy"
	},
	{
		question: "Which of the following is the same as 2010 g?",
		answers: {
			1: "2 kg 10 g",
			2: "2 kg 1 g",
			3: "20 kg 1 g",
			4: "20 kg 10 g"
		},
		correctAnswer: "1",
		difficulty: "Easy"
	},
	{
		question: "Find the value of (3y + 1) / 4 , when y = 5",
		answers: {
			1: "4",
			2: "9",
			3: "8",
			4: "5"
		},
		correctAnswer: "1",
		difficulty: "Easy"
	},
	{
		question: "The ratio of Rachel's age to Samy's age is 7 : 6. Rachel is 4 years older than Samy. What is Samy's age this year?",
		answers: {
			1: "24",
			2: "10",
			3: "11",
			4: "28"
		},
		correctAnswer: "1",
		difficulty: "Easy"
	},
	{
		question: "How many fifths are there in 2 3/5?",
		answers: {
			1: "13",
			2: "11",
			3: "3",
			4: "6"
		},
		correctAnswer: "1",
		difficulty: "Easy"
	},
	{
		question: "The sum of 1/2 and 2/5 is the same as ___.",
		answers: {
			1: "0.900",
			2: "0.009",
			3: "0.090",
			4: "9.000"
		},
		correctAnswer: "1",
		difficulty: "Easy"
	},
	{
		question: "What is the value of 36 + 24 / (9 - 3) + 2 x 5 ?",
		answers: {
			1: "50",
			2: "51",
			3: "60",
			4: "66"
		},
		correctAnswer: "1",
		difficulty: "Easy"
	},
	{
		question: "Sally has 100 marbles and her brother has 300 marbles. Express Sally's marbles as a percentage of the total number of marbles they have altogether.",
		answers: {
			1: "25%",
			2: "33 1/3 %",
			3: "300%",
			4: "400%"
		},
		correctAnswer: "1",
		difficulty: "Easy"
	},
	{
		question: "Mr Tan has an equal number of pens and pencils. He puts the pens in bundles of 8 and the pencils in bundles of 12.     There are 15 bundles altogether. How many pens are there?",
		answers: {
			1: "72",
			2: "24",
			3: "48",
			4: "96"
		},
		correctAnswer: "1",
		difficulty: "Hard"
	},
	{
		question: "3 ones, 4 tenths and 7 thousandths is ___",
		answers: {
			1: "3.407",
			2: "3.470",
			3: "3.047",
			4: "3.740"
		},
		correctAnswer: "1",
		difficulty: "Hard"
	},
	{
		question: "Which of the following is equal to 0.25%?",
		answers: {
			1: "1/400",
			2: "1/25",
			3: "1/4",
			4: "25"
		},
		correctAnswer: "1",
		difficulty: "Hard"
	}
];

// display quiz right away
buildQuiz();

// on submit, show results
submitButton.addEventListener('click', showResults);