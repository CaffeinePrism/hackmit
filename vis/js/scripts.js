
var map;
var ids = [];
var drivers = [];

var directionsDisplay;
var directionsService = new google.maps.DirectionsService();

$(document).ready(function(){
  google.maps.event.addDomListener(window, 'load', init);

  function init() {

    /* position Amsterdam */
    var latlng = new google.maps.LatLng(42.3598, -71.0921);

    var mapOptions = {
      center: latlng,
      scrollWheel: false,
      zoom: 13
    };
    
    var marker = new google.maps.Marker({
      position: latlng,
      url: '/',
      animation: google.maps.Animation.DROP,
      icon: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'
    });

    marker.addListener('click', function() {
      you_are_here();
    });
    
    map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
    directionsDisplay = new google.maps.DirectionsRenderer();
    directionsDisplay.setMap(map);
    marker.setMap(map);

    var input = document.getElementById('search');
    var searchBox = new google.maps.places.SearchBox(input);
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

    // Bias the SearchBox results towards current map's viewport.
    map.addListener('bounds_changed', function() {
      searchBox.setBounds(map.getBounds());
    });

    var markers = [];
    // Listen for the event fired when the user selects a prediction and retrieve
    // more details for that place.
    searchBox.addListener('places_changed', function() {
      var places = searchBox.getPlaces();

      if (places.length == 0) {
        return;
      }

      // Clear out the old markers.
      markers.forEach(function(marker) {
        marker.setMap(null);
      });
      markers = [];

      // For each place, get the icon, name and location.
      var bounds = new google.maps.LatLngBounds();
      places.forEach(function(place) {
        var icon = {
          url: place.icon,
          size: new google.maps.Size(71, 71),
          origin: new google.maps.Point(0, 0),
          anchor: new google.maps.Point(17, 34),
          scaledSize: new google.maps.Size(25, 25)
        };

        // Create a marker for each place.
        markers.push(new google.maps.Marker({
          map: map,
          icon: icon,
          title: place.name,
          position: place.geometry.location
        }));

        if (place.geometry.viewport) {
          // Only geocodes have viewport.
          bounds.union(place.geometry.viewport);
        } else {
          bounds.extend(place.geometry.location);
        }
      });
      map.fitBounds(bounds);
    });

  };

  update();

  setInterval(update, 5000);
});

function you_are_here() {
  $('#panel-title').html("You are here!");
  $('#items').css('display', 'none');
  $('#item1').html('Our Story');
  $('#item2').html('Who We Are');
  $('#item3').html('What We Do');
  $('#item4').html('The Next Steps');
}

function update() {

  // get positions & update markers here

  var driver = new google.maps.Marker({
    position: latlng,
    url: '/',
    animation: google.maps.Animation.DROP,
    name: 'Kevin Fu',
    items: ['coca cola can', 'sprite can', 'red bull can'],
    destination: 'boston logan airport'
  });
  drivers.push(driver);


  for(var i=0; i<drivers.length; i++) {
    drivers[i].position = new google.maps.LatLng(40.2598+Math.random(), -71.1921);
    drivers[i].setMap(map);
  }

}

function getRoute(driver) {
    var start = driver.position;
    var end = driver.destination;
    var request = {
      origin:start,
      destination:end,
      travelMode: google.maps.TravelMode.DRIVING
    };
    directionsService.route(request, function(result, status) {
      if (status == google.maps.DirectionsStatus.OK) {
        directionsDisplay.setDirections(result);
      }
    });
}