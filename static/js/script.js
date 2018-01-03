var current_data_item;
var pool_size;

$(function () {

    // init the validator
    // validator files are included in the download package
    // otherwise download from http://1000hz.github.io/bootstrap-validator

    // when the form is submitted
    $('#answer-form').on('submit', function (e) {

        // if the validator does not prevent form submit
        if (!e.isDefaultPrevented()) {
            var url = "/submit";

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
                    var newQuestion = "<h1>" + messageText + "</h1>";


                    // If we have messageAlert and messageText
                    if (messageAlert && messageText) {
                        // inject the alert to .messages div in our form
                        $('#answer-form').find('.question-display').html(newQuestion);
                        // empty the form
                        $('#answer-form')[0].reset();
                    }
                }
            });
            return false;
        }
    })
});

$(document).ready(function () {

    load_item(0);
    console.log("ready");
});


function load_item(index){
    // var dic = {};
    // dic.index = index;
    var jqxhr = $.post("/get_item", {index: index}, function (data) {
        current_data_item = data.results;
        var question_character = current_data_item.character;
        // question_character = "hello";
        $('#answer-form').find('.question-display').html("<h1 class=\"display-1\">" + question_character + "</h1>");

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

    console.log(current_data_item);
}