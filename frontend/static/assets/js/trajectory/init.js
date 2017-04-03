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
        document.getElementById("lnglat").value = e.lnglat.getLng() + ',' + e.lnglat.getLat();
        addMarker(e.lnglat.getLng(), e.lnglat.getLat());
    }
    map.on('click', _clickEventListener);

    function addMarker(longitude, latitude) {
        marker = new AMap.Marker({
            icon: "../static/assets/img/trajectory/map-marker24.png",
            position: [longitude, latitude]
        });
        marker.setMap(map);

        // remove map-marker
        AMap.event.addListener(marker, 'click', function(e) {
            map.remove(e.target);
        });
    }

    var clickEventListener = map.on('click', function(e) {
        document.getElementById("lnglat").value = e.lnglat.getLng() + ',' + e.lnglat.getLat()
    });

    // Autocomplete Search Box
    AMap.plugin(['AMap.Autocomplete', 'AMap.PlaceSearch'], function() {
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


})
