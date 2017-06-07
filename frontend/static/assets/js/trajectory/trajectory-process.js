var regionCity = 'Shanghai';
var map;

var markers = {}
var pointCount = 0;
var formCount = 0;
var isMarkerSearched = false;

var trajectoryPoints = [];
var date;
var trajectoryPath;

var strokeColors = ['#CD2626', '#3366FF', '#458B74',]

$(document).ready(function () {

    // load the map
    map = new AMap.Map('map-container', {
        resizeEnable: true,
        scrollWheel: false,
        center: [121.476764, 31.225834],
        zoom: 11,
        lang: 'zh_en'
    });

    map.plugin(["AMap.ToolBar"], function () {
        map.addControl(new AMap.ToolBar());
    });

    // click the map to get the longitude and latitude
    var _clickEventListener = function (e) {

        var lng = e.lnglat.getLng();
        var lat = e.lnglat.getLat();

        var lnglat = document.getElementById("lng_lat");
        $("#lng_lat").attr({"placeholder": "", "value": lng + "," + lat})
        addMarker(lng, lat);
    }
    map.on('click', _clickEventListener);


    // Add Location markers on the map
    function addMarker(longitude, latitude) {

        // Guarantee when adding markers, there is no point in trajectory points

        if (isMarkerSearched) {
            map.clearMap();
            isMarkerSearched = false;
        }

        if (Object.keys(trajectoryPoints).length != 0) {
            map.clearMap();
            trajectoryPoints = [];
        }


        marker = new AMap.Marker({
            icon: "../static/assets/img/trajectory/map-marker24.png",
            position: [longitude, latitude]
        });
        console.log("yes");
        marker.setMap(map);
        markers[pointCount] = [longitude, latitude];
        pointCount += 1;

        // remove map-marker
        AMap.event.addListener(marker, 'click', function (e) {
            var position = e.target.getPosition();
            var lng = position['lng'], lat = position['lat'];
            for (key in markers) {
                pos = markers[key];
                if (pos[0] == lng && pos[1] == lat) {
                    console.log(lng + " " + lat);
                    delete markers[key];
                    break;
                }
            }
            map.remove(e.target);
        });
    }

    // Autocomplete Search Box
    map.plugin(['AMap.Autocomplete', 'AMap.PlaceSearch'], function () {
        var autoOptions = {
            city: regionCity, // specify the search region
            input: "tipinput"
        };
        autocomplete = new AMap.Autocomplete(autoOptions);
        var placeSearch = new AMap.PlaceSearch({
            // city: regionCity,
            map: map
        })
        AMap.event.addListener(autocomplete, "select", function (e) {
            //TODO Personalized function
            if (e.poi && e.poi.location) {
                map.setZoom(12);
                map.setCenter(e.poi.location);
            }
            // Show some potential points
            //placeSearch.search(e.poi.name)
        });
    });

    // from input
    map.plugin(['AMap.Autocomplete', 'AMap.PlaceSearch'], function () {
        var autoOptions = {
            city: regionCity, // specify the search region
            input: "dir_from_ipt"
        };
        autocomplete = new AMap.Autocomplete(autoOptions);
        var placeSearch = new AMap.PlaceSearch({
            city: regionCity,
            map: map
        })
        AMap.event.addListener(autocomplete, "select", function (e) {
            //TODO Personalized function
            if (e.poi && e.poi.location) {
                map.setZoom(14.5);
                map.setCenter(e.poi.location);
            }
            // Show some potential points
            //placeSearch.search(e.poi.name)
        });
    });

    // to input
    map.plugin(['AMap.Autocomplete', 'AMap.PlaceSearch'], function () {
        var autoOptions = {
            city: regionCity, // specify the search region
            input: "dir_to_ipt"
        };
        autocomplete = new AMap.Autocomplete(autoOptions);
        var placeSearch = new AMap.PlaceSearch({
            city: regionCity,
            map: map
        })
        AMap.event.addListener(autocomplete, "select", function (e) {
            //TODO Personalized function
            if (e.poi && e.poi.location) {
                map.setZoom(14.5);
                map.setCenter(e.poi.location);
            }
            // Show some potential points
            //placeSearch.search(e.poi.name)
        });
    });

    // Display the history trajectory
    $(function () {
        $(".details").each(function () {
            $(this).click(function () {
                // Gurantee when display the trajectory points, there is markers
                if (Object.keys(markers).length != 0) {
                    markers = {};
                }
                map.clearMap();
                trajectoryPoints = [];
                date = $(this).attr("id").split(" ")[1].substring(0, 2)
                trajectoryPath = $(this).attr("id") + ".txt";

                $.post(
                    'display',
                    {filepath: trajectoryPath},
                    function (data) {

                        // assign the trajectory displayed for searching
                        trajectoryPoints = data.slice(0);
                        var polyline = new AMap.Polyline({
                            path: data, //设置线覆盖物路径 #
                            strokeColor: '#000000', //线颜色
                            strokeOpacity: 1, //线透明度
                            strokeWeight: 8, //线宽
                            strokeStyle: "solid", //线样式
                            strokeDasharray: [10, 5] //补充线样式
                        });
                        map.setZoom(11);
                        map.setCenter(data[Object.keys(data).length / 2]);
                        polyline.setMap(map);
                    },
                    'json'
                );
            });
        });
    });

});

// Search Part
function _search() {
    var temp, type;
    var date = document.getElementById("date").value;
    if (Object.keys(markers).length == 0) {
        temp = trajectoryPoints;
        type = 't'
        //date = '2015-04-02'
    } else {
        temp = markers;
        type = 'p';
        //date = '2015-04-02';
    }
    $.post(
        'search',
        {
            queryPoints: JSON.stringify(temp),
            queryType: type,
            queryDate: date
        },
        function (data) {

            trajectoryRes = data[0];
            pointsRes = data[1];

            $('#searching-result-display').empty();
            $.each(trajectoryRes, function (index) {
                var resultContent = "<div class=\"desc\"><div class=\"thumb\"<span class=\"badge bg-theme\"><i class=\"fa fa-clock-o\"></i></span></div><div class=\"details\"><h style='color:" + strokeColors[index] +"'>" + trajectoryRes[index] + "</h></div></div>";
                $("#searching-result-display").append(resultContent);
            });

            $.each(pointsRes, function (index) {
                var pathData = pointsRes[index];
                var polyline = new AMap.Polyline({
                    path: pathData, //设置线覆盖物路径 #
                    strokeColor: strokeColors[index], //线颜色
                    strokeOpacity: 2, //线透明度
                    strokeWeight:  5 - (index), //线宽
                    strokeStyle: "dashed", //线样式
                    strokeDasharray: [10, 5] //补充线样式
                });
                polyline.setMap(map);
            })
            map.setZoom(11);
            // map.setCenter([121.47199, 31.231973]);
        },
        'json'
    );

    //TODO
    isMarkerSearched = true;
    markers = {};
}

function _searchFormAppend() {
    formCount += 1;
    var inputId = 'input-' + formCount;
    var content = "<p class=\"line_serch_ipt line-search-point\"><label>途径  </label><input type=\"text\" class=\"dir_ipt\" id=\"" + inputId + "\" dirtype=\"from\" placeholder=\"请输入途径点\" value=\"\" autocomplete=\"off\" style=\"text-align: center\"></p>"

    $(".passList").append(content);
    map.plugin(['AMap.Autocomplete', 'AMap.PlaceSearch'], function () {
        var autoOptions = {
            city: regionCity, // specify the search region
            input: inputId
        };
        autocomplete = new AMap.Autocomplete(autoOptions);
        var placeSearch = new AMap.PlaceSearch({
            city: regionCity,
            map: map
        })
        AMap.event.addListener(autocomplete, "select", function (e) {
            //TODO Personalized function
            if (e.poi && e.poi.location) {
                map.setZoom(14.5);
                map.setCenter(e.poi.location);
            }
        });
    });
}

function _searchFormRemove() {
//    var pId = 'p' + formCount;
    var passList = document.getElementsByClassName('passList')[0]
    if (passList.lastChild) {
        passList.removeChild(passList.lastChild);
        formCount -= 1;
    }
}

function _searchFormReset() {
    map.clearMap();
    markers = {}
    pointCount = 0;
    isMarkerSearched = false;
    trajectoryPoints = [];

    $("#lng_lat").attr({"placeholder": "经纬度坐标", "value": ""})
    $("#dir_from_ipt").attr({"placeholder": "请输入起点", "value": ""})
    //$("#dir_to_ipt").attr({"placeholder":"请输入终点", "value": ""})
    $("#dir_to_ipt").val("")
    console.log($("#dir_to_ipt").val())

    for (var i = 1; i <= formCount; i++) {
        var inputId = "#input-" + i;
        $(inputId).attr({"placeholder": "请输入起点", "value": ""})
    }
}