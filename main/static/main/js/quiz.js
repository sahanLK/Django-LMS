/*
 ======================================
 *          UCR QUIZ SYSTEM
 *
 *      Author: SAHAN LAKSHITHA
 ======================================
*/

$(document).ready(function() {
    const answersMap = {
        1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F',
    }

    // Add New Question
    $('#questionCreateBtn').on('click', function() {
        var quizForm = $(this).closest('#quizForm');
        var questionsArea = $(quizForm).find('#questionsArea');
        var noOfQuestions = $(quizForm).find('.question').length + 1;

        // Update the no of questions text in quiz top
        $('#noOfQuestions').text(noOfQuestions);

        var questionField = `
            <div class='row mt-4 question mb-3 pb-4 pt-3 rounded' style='background-color: #f2f2f2;'>
                <div class='col-12'>
                    <a class='roboto-title text-primary d-block mb-2 float-right' id='addAnswerBtn' style='margin-right: 40px;'>Add Answer</a>
                    <div class="input-group mb-3">
                        <div class="input-group-prepend m-auto pr-3">
                            <b class='roboto-title-muted' id='questionNumber'>${noOfQuestions} )</b>
                        </div>
                        <textarea rows=2 class='form-control' question-id='${noOfQuestions}'></textarea>
                        <div class="input-group-append m-auto pl-2" style='width: 35px;'>
                            <a class="btn" type="button" id='deleteQuestionBtn'>
                                <i class="fas fa-trash-alt text-danger"></i>
                            </a>
                        </div>
                    </div>
                    <div class='row m-0 pt-3 answers-row w-100'>
                        <div class='col-12 p-0' id='answersRow'>
                            <!-- All the answers goes here -->
                        </div>
                    </div>
                </div>
            </div>`;

        questionsArea.append(questionField);
    });

    // Delete a Question
    $('#quizForm').on('click', '#deleteQuestionBtn', function() {
        // Confirm deletion.
        if (confirm( "Delete Question ?" ) == false) {
            return;
        }

        var questionToDelete = $(this).closest('.question');
        var quizForm = $(questionToDelete).closest('#quizForm');

        $(questionToDelete).remove();

        // Update the no of questions text in quiz top
        var noOfQuestions = $(quizForm).find('.question').length;
        $('#noOfQuestions').text(noOfQuestions);

        var otherQuestions = $(quizForm).find('.question')

        // Reorder other questions accordingly, after deleting a question.
        // Most importantly update the question-id attribute.
        $(otherQuestions).each(function(index, item) {
            var newQuestionId = index + 1 ;
            $(item).find('#questionNumber').text(newQuestionId + ' )');
            $(item).find('textarea').attr({'question-id': newQuestionId});

            // Update the name attribute value with correct question-id of all answers of the question.
            var allAnswers = $(item).find('.answer-input');
            $(allAnswers).each(function() {
                $(this).attr({'q-id': newQuestionId});
            });
        });
    });

    // Add an Answer
    $('#quizForm').on('click', '#addAnswerBtn', function() {
        var relatedQuestion = $(this).closest('.question');
        var relatedQuestionTextArea = $(relatedQuestion).find('textarea');
        var relatedQuestionId = $(relatedQuestionTextArea).attr('question-id');
        var answersElem = $(relatedQuestion).find('#answersRow');

        console.log(answersElem);

        var currentAnswersCount = $(answersElem).find('.answer').length + 1;

        // Do not allow more than 6 answers for a question.
        if ( currentAnswersCount > 6 ) {
            alert("Only 6 answers are allowed per one question");
            return;
        }

        let answerItem = `
            <div class='row w-100 m-0 mb-2 answer'>
                <div class='col-1'></div>
                <div class='col-11'>
                    <div class="input-group">
                        <div class='input-group-prepend m-auto'>
                            <p class='btn btn-secondary roboto-title-muted m-0 text-white' id='answerLetter'>
                                ${answersMap[currentAnswersCount]}
                            </p>
                        </div>

                        <input type='text'
                            name='answer-${answersMap[currentAnswersCount]}'
                            q-id=${relatedQuestionId}
                            letter=${answersMap[currentAnswersCount]}
                            correct=false
                            class='form-control answer-input'>
                        <div class="input-group-append m-auto">
                            <a class='btn text-secondary make-correct-answer answer-stat-toggle'>
                                <i class="fas fa-check-circle fa-lg"></i>
                            </a>
                            <a class='btn text-white delete-answer'>
                                <i class="fas fa-trash-alt text-danger"></i>
                            </a>
                        </div>
                    </div>
                </div>
            </div>`;

        $(answersElem).append(answerItem);
        console.log("Done");
    });

    // Delete an Answer
    $('#quizForm').on('click', '.delete-answer', function() {
        if ( confirm("Delete Answer ?") == false ) {
            return;
        }

        var answerToDelete = $(this).closest('.answer'); // get the parent with class <answer>
        var question = $(answerToDelete).closest('.question');   // get the question of this answer
        answerToDelete.remove();

        // Reorder properly other answer's letters and name attribute with correct answer letter.
        var allAnswers = $(question).find('.answer');

        $(allAnswers).each(function(index, elem) {
            $(elem).find('#answerLetter').text(answersMap[index + 1]);
            var answerInputField = $(elem).find('input');
            $(answerInputField).attr({'q-id': index});
            $(answerInputField).attr({'letter': answersMap[index + 1]});
        });
    });

    // Toggle answer status between correct and incorrect
    $('#quizForm').on('click', '.answer-stat-toggle', function() {
        $(this).toggleClass('incorrect');

        // Answer input field related
        var answerInput = $(this).closest('.answer').find('input');
        if ( $(answerInput).attr('correct') == 'false' ) {
            $(answerInput).attr({'correct': true});
            $(answerInput).addClass('bg-success text-light');
            $(this).find('i').addClass('text-success');
        } else {
            $(answerInput).attr({'correct': false});
            $(answerInput).removeClass('bg-success text-light');
            $(this).find('i').removeClass('text-success');
        }

    });

    // Saving the created quiz form by the lecturer
    $('#quizQuestionsCreateBtn').on('click', function() {
        let button = $(this);
        var form = $(this).closest('#quizForm');

        // Do not create or update the quiz if empty fields exists
        if ( emptyFieldsExists(form) ) {
            alert("Please remove all the empty input fields.");
            return;
        }

        var qObjects = getQObjects(form);

        // Calling the django view_func: <quiz_questions_and_answers_view>
        $.ajax({
            type: 'POST',
            url: $(this).attr('data-url'),
            data: {
                dom: JSON.stringify({'dom': qObjects}),
                csrfmiddlewaretoken: $(this).closest('#quizForm').find('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function(response) {
                if (response.msg == 'responses-available') {
                    alert("Update are not allowed after students made responses");
                    location.reload();
                    return;
                }
                window.location.href = button.attr('data-url');
            },
            error: function(response) {
                console.log("Request failed");
            },
        });
    });

    /*
    Used to detect if empty fields exists in the quiz form.
    Lecturer not allowed to create or update a quiz with empty fields
    */
    function emptyFieldsExists(form) {
        var emptyFound = false;
        // check all the question fields
        $( $(form).find('textarea') ).each( function(index, elem) {
            if ( $.trim($(elem).val()) == '' ) {
                console.log('Empty question found');
                emptyFound = true;
            }
        });

        // check all the answer fields
        $( $(form).find('input') ).each( function(index, elem) {
            if ( $.trim($(elem).val()) == '' ) {
                console.log('Empty answer found');
                emptyFound = true;
            }
        });
        return emptyFound;
    }

    // Student making a response for quiz
    $('#quizStudentResponseCreateBtn').on('click', function() {
        form = $(this).closest('#quizForm');
        var qObjects = getQObjects(form);

        // Calling the django view_func: <quiz_live_view>
        $.ajax({
            type: 'POST',
            url: $(this).attr('data-url'),
            data: {
                dom: JSON.stringify({'dom': qObjects}),
                csrfmiddlewaretoken: $(this).closest('#quizForm').find('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function(response) {
                window.location.href = $('#redirectFromQuizLive').val();
            },
            error: function(response) {
                console.log("Request failed");
            },
        });
    });


    function getQObjects(form) {
        /*
        RETURNS QUESTION OBJECTS

        These question objects consists the details of all the questions and the answers
        related to that particular questions.

        used by both students as well as lecturers.
            STUDENTS -> For making a response for the quiz.
            LECTURERS -> For creating/updating the quiz questions.
        */
        var qObjects = [];

        $( $(form).find('.question') ).each(function(index, elem) {
            var questionTextArea = $(elem).find('textarea');
            var questionText = $(questionTextArea).val();
            var questionId = $(questionTextArea).attr('question-id');

            // Creating question object
            var question = {
                'question-id': questionId,
                'text': questionText,
            }

            // Creating objects with all the answers elated to the above question
            var answers = [];
            $( $(elem).find('.answer-input') ).each(function(index, elem) {
                var questionId = $(elem).attr('q-id');
                var letter = $(elem).attr('letter');
                var text = $(elem).val();
                var correct = $(elem).attr('correct');

                var answer = {
                    'questionId': questionId,
                    'letter': letter,
                    'text': text,
                    'correct': correct,
                }
                answers.push(answer);
            });

            // Creating a question object with the question ans all the answers
            var qObject = {
                'question': question,
                'answers': answers,
            }
            qObjects.push(qObject);
        });
        return qObjects;
    }
});