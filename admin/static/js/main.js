$(function() {
    function fixSize(element) {
        element.css("width", element.val().length * 11);
    }

    $("input[type=text]").on("keypress", function() {
        console.debug($(this).val());
        fixSize($(this));
    });

    $("input[type=text]").each(function() {
        fixSize($(this));
    });

    $(".check-all").on("click", function() {
        $("input[type=checkbox]").prop("checked", $(this).prop("checked"));
    });

    $("#delete-multi").on("click", function(event) {
        event.preventDefault();

        if (!confirm("Это навсегда. Точно удалить?")) return;

        var ids = [];
        $(".rows input[type=checkbox]:checked").each(function() {
            var id = $(this).attr("data-id");
            if (id) {
                ids.push(id);            
            }
        });
        location.href = $(this).attr("href") + "?ids=" + ids.join(",")
    });
});
