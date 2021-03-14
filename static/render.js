$(function () {
    $('td').each(function (i, v) {
        if (v.textContent === "done") {
            v.title = "Accept"
            v.bgColor = "#D4EDC9"

        } else if (v.textContent === 'check') {
            v.title = "First blood"
            v.bgColor = "#80ff80"
        } else if (v.textContent[0] === 'h') {
            v.title = "N/A"
            v.bgColor = "#E5E5E5"
        } else {
            v.bgColor = "#FFE3E3"
            if (v.textContent[0] === 'b') {
                v.title = "Runtime Error"
            } else if (v.textContent[0] === 'd') {
                v.title = "Memory Limit Exceeded"
            } else if (v.textContent[0] === 'a') {
                v.title = "Time Limit Exceeded"
            } else if (v.textContent[0] === 'f') {
                v.title = "Output Limit Exceeded"
            } else {
                v.title = "Wrong Answer"
            }
        }
    })
    $('thead > tr > th').each(function (i, v) {
        v.onclick = function () {
            window.open("https://oj.nctu.me/problems/" + v.textContent + "/", "_blank")
        }
    })
    $('tbody > tr > td').each(function (i, v) {
        v.onclick = function () {
            var p = v.parentNode.firstElementChild.textContent
            var c = $('thead > tr > th').get(v.cellIndex).textContent
            window.open("https://oj.nctu.me/groups/" + $('text').text() + "/submissions/?count=100000&name=" + p + "&problem_id=" + c, "_blank")
        }
    })
})
