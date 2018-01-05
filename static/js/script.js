var current_data_item;
var current_index;
var pool_size;

$(function () {

    // init the validator

    // when the form is submitted
    $('#answer-form').on('submit', function (e) {

        // if the validator does not prevent form submit
        if (!e.isDefaultPrevented()) {
            var url = "/submit";
            var correct = false;
            var answer = $("#answer")[0].value;

            var correct_answer = get_answer();
            for (i = 0; i < correct_answer.length; i++) {
                if (strcmp(answer, correct_answer[i]) === 0) {
                    correct = true;
                }
            }

            if (correct) {
                next_item()
            } else {
                var messageText = "You entered: " + answer + ", Correct answer is " + correct_answer[0] + "";
                //class="close" data-dismiss="alert" &times;
                var alertBox = '<div class="alert ' + 'text-center alert-danger alert-dismissable"><button id="wrong-next" type="button" onclick="next_item()" class="close" aria-hidden="true"><i class="fas fa-angle-right"></i></button> <h4>' + messageText + '</h4></div>';
                $('#message-display').html(alertBox);
                $('#wrong-next').focus();

            }


            // POST values in the background the the script URL
            $.ajax({
                type: "POST",
                url: url,
                data: $(this).serialize(),
                success: function (data) {
                    // data = JSON object that contact.php returns

                    // we recieve the type of the message: success x danger and apply it to the
                    var messageAlert = 'alert-' + data.type;
                    var messageText = data.message;

                    // let's compose Bootstrap alert box HTML
                    // var newQuestion = "<h1>" + messageText + "</h1>";

                    $('#answer-form')[0].reset();
                    // If we have messageAlert and messageText
                    // if (messageAlert && messageText) {
                    //     // inject the alert to .messages div in our form
                    //     // $('#answer-form').find('.question-display').html(newQuestion);
                    //     // empty the form
                    //     $('#answer-form')[0].reset();
                    // }
                }
            });
            return false;
        }
    })
});

$(document).ready(function () {
    current_index = 0;
    get_pool_size();
    load_item(current_index);


    console.log("ready!");
});


function get_answer() {
    var correct_answer;
    if (strcmp(current_data_item.type, 'kanji') === 0) {

        if ("onyomi".localeCompare(current_data_item.important_reading) === 0) {
            correct_answer = current_data_item.onyomi;

        } else if (strcmp("kunyomi", current_data_item.important_reading) === 0) {
            correct_answer = current_data_item.kunyomi;
        }

    } else if (strcmp(current_data_item.type, 'vocabulary') === 0) {
        correct_answer = current_data_item.kana;
    }

    return correct_answer;
}


function next_item() {
    if(current_index < (pool_size-1)) {
        current_index = current_index + 1;
    }else{
        current_index = 0;
    }
    load_item(current_index);
    $('#answer').focus();
}


function previous_item() {
    if(current_index > 0) {
        current_index = current_index - 1;
    }else{
        current_index = pool_size -1;
    }
    load_item(current_index);
    $('#answer').focus();
}


function show_answer() {
    //  TODO: make this function work for whe you get the answer wrong as well

    var correct_answer = get_answer();

    var messageText = "The correct answer is " + correct_answer[0] + "";
    var alertBox = '<div class="alert ' + 'text-center alert-info alert-dismissable"><button id="answer-dismiss" type="button" data-dismiss="alert" class="close" aria-hidden="true">&times</button>' + messageText + '</div>';
    $('#message-display').html(alertBox);
    $('#answer-dismiss').focus();
}

function show_info() {
    window.open(current_data_item.url)
}

function get_pool_size() {
    var jqxhr = $.post("/get_pool_details", function (data) {
        pool_size = parseInt(data.pool_length);
    })
        .done(function () {

        })
        .fail(function () {
            console.log("error");
        })
        .always(function () {
            console.log("complete");
        });

}


function load_item(index) {
    // var dic = {};
    // dic.index = index;
    var jqxhr = $.post("/get_item", {index: index}, function (data) {

        current_data_item = data.results;
        var question_character = current_data_item.character;
        // question_character = "hello";

        var question_type_html = "<h6 class=\"card-text txt-question-type\">" + capFirstLetter(current_data_item.type) + "</h6>\n" +
            "                        <p class=\"txt-question-type font-weight-bold\">" + "Reading" + "</p>";

        update_question_background(current_data_item.type);
        $('#answer-form').find('.question-display').html("<h1 class=\"display-1 card-text\">" + question_character + "</h1>");
        $('#answer-form').find('.question-type-display').html(question_type_html);


        $('#message-display').html("");

        update_progress_bar(index);
        console.log("success");
    })
        .done(function () {
            console.log("second success");
        })
        .fail(function () {
            console.log("error");
        })
        .always(function () {
            console.log("complete");
        });

    // console.log(current_data_item);
}


function update_question_background(question_type) {

    if ("vocabulary".localeCompare(question_type)) {
        $("#question-card").removeClass('bg-radicals-grad bg-kanji-grad bg-vocabulary-grad').addClass('bg-vocabulary-grad');
    } else if ("kanji".localeCompare(question_type)) {

        $("#question-card").removeClass('bg-radicals-grad bg-kanji-grad bg-vocabulary-grad').addClass('bg-kanji-grad');
    } else if ("radical".localeCompare(question_type)) {

        $("#question-card").removeClass('bg-radicals-grad bg-kanji-grad bg-vocabulary-grad').addClass('bg-radicals-grad');
    }
}


function update_progress_bar(index) {
    $('.progress-bar')[0].style.width = String((index / (pool_size - 1)) * 100) + "%";
}


function capFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function strcmp(str1, str2) {
    // http://kevin.vanzonneveld.net
    // +   original by: Waldo Malqui Silva
    // +      input by: Steve Hilder
    // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
    // +    revised by: gorthaur
    // *     example 1: strcmp( 'waldo', 'owald' );
    // *     returns 1: 1
    // *     example 2: strcmp( 'owald', 'waldo' );
    // *     returns 2: -1

    return ( ( str1 == str2 ) ? 0 : ( ( str1 > str2 ) ? 1 : -1 ) );
}