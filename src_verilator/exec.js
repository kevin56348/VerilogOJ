function collapse(number_test, total_num) {
    let ele = document.getElementById("svg_wave_" + number_test);
    if (ele == null) {
        return;
    }
    if (ele.style.display !== "none") {
        ele.style.display = "none";
    } else {
        for (let i = 0; i <= total_num; i++) {
            ele = document.getElementById("svg_wave_" + i);
            if (ele != null) {
                ele.style.display = "none";
            }
        }
        ele = document.getElementById("svg_wave_" + number_test);
        if (ele.style.display !== "none") {
            ele.style.display = "none";
        } else {
            ele.style.display = "block";
        }
    }
}