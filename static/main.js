$(function () {
    var $grid = $(".pic-grid").masonry({
        itemSelector: '.pic-grid-item',
        percentPosition: true
    });
    $grid.imagesLoaded().progress( function() {
        $grid.masonry('layout');
    });

    $('#fileupload').fileupload({
        dataType: 'json',
        done: function (e, data) {
            $.each(data.result.files, function (index, file) {
                $('<img>').attr("src", file.url).appendTo($('.main'));
                $('<p></p>').text(file.name).appendTo($('.main'));
                old_val = $('#img_list').val();
                if (old_val === "") {
                    new_val = file.name;
                } else {
                    new_val = old_val + ";" + file.name;
                }
                $('#img_list').val(new_val);
            });
        },
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $('#progress .bar').css(
                'width',
                progress + '%'
            );
        }
    });

    $('#fileupload-overview').fileupload({
        dataType: 'json',
        done: function (e, data) {
            $.each(data.result.files, function (index, file) {
                $.post(".", {img_list: file.name}, function(data){
                    // TODO hier jedes Bild dynamisch (besser als jetzt) ankleben
                    $('<img>').attr("src", file.url).appendTo($('.main'));
                    $('<p></p>').text(file.name).appendTo($('.main'));
                });
            });
        },
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $('#progress .bar').css(
                'width',
                progress + '%'
            );
        }
    });

    $("#yes-btn").click(function(e){
        $.ajax(".", {
            data: {rating: "yes"},
            type: "post",
            success: function(d){
                window.location = d.next;
            },
            error: function(d){
                alert("Fehler! " + d.responseJSON.error);
            },
        });
    });

    $("#no-btn").click(function(e){
        $.ajax(".", {
            data: {rating: "no"},
            type: "post",
            success: function(d){
                window.location = d.next;
            },
            error: function(d){
                alert("Fehler! " + d.responseJSON.error);
            },
        });
    });

    $("#unsafe-btn").click(function(e){
        var comment = prompt("Warum unsicher?");
        if (comment !== "") {
            $.ajax(".", {
                data: {rating: "unsafe", comment: comment},
                type: "post",
                success: function(d){
                    window.location = d.next;
                },
                error: function(d){
                    alert("Fehler! " + d.responseJSON.error);
                },
            });
        }
    });

    $("#delete-img").click(function(e){
        if (confirm("Dieses Bild löschen?")) {
            var href = $("#delete-img").data("target");
            $.ajax(href, {
                type: "delete",
                success: function(d){
                    window.location = d.next;
                },
                error: function(d){
                    alert("Fehler! " + d.responseJSON.error);
                },
            });
        }
    });
});