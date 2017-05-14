/**
 * Created by luhongyu on 2017/5/6.
 */

//获取控件左绝对位置

function getAbsoluteLeft(o) {
    //o = document.getElementById(objectId);
    oLeft = o.offsetLeft;
    while (o.offsetParent != null) {
        oParent = o.offsetParent;
        oLeft += oParent.offsetLeft;
        o = oParent;
    }
    return oLeft;
}
//获取控件上绝对位置
function getAbsoluteTop(o) {
    //o = document.getElementById(objectId);
    oTop = o.offsetTop;
    while (o.offsetParent != null) {
        oParent = o.offsetParent;
        oTop += oParent.offsetTop;  // Add parent top position
        o = oParent;
    }
    return oTop;
}

//获取控件宽度
function getElementWidth(x) {
    //x = document.getElementById(objectId);
    return x.offsetWidth;
}

function getElemenHeight(x) {
    //x = document.getElementById(objectId);
    return x.offsetHeight;
}