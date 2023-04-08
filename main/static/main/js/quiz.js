$(document).ready(function() {

    const answersMap = {
        1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F',
    }

    // Add New Question
    $('#questionCreateBtn').on('click', function() {
        var quizForm = $(this).closest('#quizForm');
        var noOfQuestions = $(quizForm).find('.question').length + 1;

        var questionField = `
            <div class='question p-2 border mb-3'>
                <div class='row m-0 pb-3'>
                    <div class='col-12 p-0 text-right'>
                        <a class='roboto-title text-primary pl-2 pr-2' id='addAnswerBtn'>Add Answer</a>
                        <a class='roboto-title text-danger pl-2 pr-2' id='deleteQuestionBtn'><i class="fas fa-trash-alt"></i></a>
                    </div>
                </div>
                <div class='row m-0 p-0'>
                    <div class='col-1 mt-auto mb-auto mw-100'>
                        <b class='roboto-title-muted' id='questionNumber'>${noOfQuestions} )</b>
                    </div>
                    <div class='col-11 p-0'>
                        <textarea rows=2 class='form-control'></textarea>
                    </div>
                </div>
                <div class='row m-0 pt-3 answers-row w-100'>
                    <div class='col-12 p-0' id='answersRow'>
                        <!-- All the answers goes here -->
                    </div>
                </div>
            </div>`;

        quizForm.append(questionField);
    });

    // Delete a Question
    $('#quizForm').on('click', '#deleteQuestionBtn', function() {
        // Confirm question deletion.
        if (confirm( "Delete Question ?" ) == false) {
            return;
        }

        var questionToDelete = $(this).closest('.question');
        var quizForm = $(questionToDelete).closest('#quizForm');

        $(questionToDelete).remove();
        var otherQuestions = $(quizForm).find('.question')

        // Reorder other questions accordingly, after deleting a question.
        $(otherQuestions).each(function(index, item) {
            $(item).find('#questionNumber').text(index+1 + ' )');
        });
    });

    // Add an Answer
    $('#quizForm').on('click', '#addAnswerBtn', function() {
        var answersElem = $(this).closest('.question').find('#answersRow');
        var currentAnswersCount = $(answersElem).find('.answer').length + 1;

        // Do not allow more than 6 answers for a question.
        if ( currentAnswersCount > 6 ) {
            alert("Only 6 answers are allowed per one question");
            return;
        }

        let answerItem = `
            <div class='row w-100 m-0 mb-2 answer'>
                <div class='col-1 mt-auto mb-auto'>
                </div>
                <div class='col-1 mt-auto mb-auto' id=''>
                    <p class='roboto-title-muted' id='answerLetter'>${answersMap[currentAnswersCount]} .</p>
                </div>
                <div class='col-7 p-0 mt-auto mb-auto' id='answersCol'>
                    <input type='text' class='form-control' letter=${answersMap[currentAnswersCount]} correct=false>
                </div>
                <div class='col-3 mt-auto mb-auto' id=''>
                    <a class='text-danger make-correct-answer mr-2'><i class="fas fa-check-circle text-success"></i></a>
                    <a class='text-danger make-incorrect-answer mr-2'><i class="fas fa-times-circle text-danger"></i></a>
                    <a class='text-danger delete-answer mr-2'>delete</a>
                </div>
            </div>`;
        $(answersElem).append(answerItem);
    });

    // Delete an Answer
    $('#quizForm').on('click', '.delete-answer', function() {
        var answerToDelete = $(this).parent().parent(); // get the parent with class <answer>
        var question = $(answerToDelete).parent().parent().parent();   // get the question of this answer
        answerToDelete.remove();

        // Reorder properly other answer's letters and also attribute values
        var allAnswers = $(question).find('.answer');
        $(allAnswers).each(function(index, elem) {
            $(elem).find('#answerLetter').text(answersMap[index+1]);
            $(elem).find('input').attr({'letter': answersMap[index+1]});
        });
    });

});