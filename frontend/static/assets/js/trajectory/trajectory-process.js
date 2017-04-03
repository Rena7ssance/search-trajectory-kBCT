$(document).ready(function() {

    var regionCity = 'Shanghai';

    // load the map
    var map = new AMap.Map('map-container', {
        resizeEnable: true,
        scrollWheel: false,
        center: [121.476764, 31.225834],
        zoom: 11,
        lang: 'zh_en'
    });

    map.plugin(["AMap.ToolBar"], function() {
        map.addControl(new AMap.ToolBar());
    });

    // click the map to get the longitude and latitude
    var _clickEventListener = function(e) {
        var lng = e.lnglat.getLng();
        var lat = e.lnglat.getLat();
        document.getElementById("lnglat").value = lng + ',' + lat;
        addMarker(lng, lat);
    }
    map.on('click', _clickEventListener);

    var markers = {}
    var pointCount = 0;
    function addMarker(longitude, latitude) {
        marker = new AMap.Marker({
            icon: "../static/assets/img/trajectory/map-marker24.png",
            position: [longitude, latitude]
        });
        marker.setMap(map);
        markers[pointCount] = [longitude, latitude];
        pointCount += 1;

        // remove map-marker
        AMap.event.addListener(marker, 'click', function(e) {
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
    map.plugin(['AMap.Autocomplete', 'AMap.PlaceSearch'], function() {
        var autoOptions = {
            city: regionCity, // specify the search region
            input: "tipinput"
        };
        autocomplete = new AMap.Autocomplete(autoOptions);
        var placeSearch = new AMap.PlaceSearch({
            // city: regionCity,
            map: map
        })
        AMap.event.addListener(autocomplete, "select", function(e) {
            //TODO Personalized function
            if (e.poi && e.poi.location) {
                map.setZoom(12);
                map.setCenter(e.poi.location);
            }
            // Show some potential points
            //placeSearch.search(e.poi.name)
        });
    });


    var strokeColors = ['#CD2626', '#458B74', '#3366FF',]
    $("#button").click(function(){
//        console.log(Object.keys(markers).length);
        var temp, type;
        if (markers.length != 0) {
            temp = trajectoryPoints;
            type = 't'
        } else {
            temp = markers;
            type ='p'
        }


        $.post(
            'search',
            {
                queryPoints: JSON.stringify(temp),
                queryType: type
            },
            function(data) {
                $.each(data, function(index) {
                    var pathData = data[index];
                    var polyline = new AMap.Polyline({
                            path: pathData, //设置线覆盖物路径 #
                            strokeColor: strokeColors[index], //线颜色
                            strokeOpacity: 2, //线透明度
                            strokeWeight: 6-(index*2), //线宽
                            strokeStyle: "solid", //线样式
                            strokeDasharray: [10, 5] //补充线样式
                        });
                     polyline.setMap(map);
                })
            },
            'json'
        );

        //TODO
        markers = []
    })

    var trajectoryPoints;
    $("#traj-btn").click(function(){
        $.post(
            'display',
            {filepath: $("#traj-btn").text()},
            function(data) {

                // assign the trajectory displayed for searching
                trajectoryPoints = data.slice(0);
                var polyline = new AMap.Polyline({
                    path: data, //设置线覆盖物路径 #
                    strokeColor: '#000000', //线颜色
                    strokeOpacity: 1, //线透明度
                    strokeWeight: 6, //线宽
                    strokeStyle: "solid", //线样式
                    strokeDasharray: [10, 5] //补充线样式
                });
                map.setZoom(13);
                map.setCenter(data[data.length/2]);
                polyline.setMap(map);
            },
            'json'
        );
    })


    function reset() {
        map.clearMap();
        markers = [];
    }
})
