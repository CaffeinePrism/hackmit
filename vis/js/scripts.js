
var map;
var drivers = [];
var waiting = [];
var done = [];

var customer = 'cus_KUs0WGz_I6R-V-';
var api_key = 'b8e63d64-541a-4e72-a02b-619aa23f27fa';

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
      icon: 'http://maps.google.com/mapfiles/ms/icons/purple-dot.png'
    });

    marker.addListener('click', function() {you_are_here();});
    
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
  $('#item1').html('Our Motive');
  $('#par1').html('Everyday, millions of people all across the globe struggle with hunger. Meanwhile, thousands of pounds of leftover food go to waste everyday. Our goal is to use the advances of modern technology to bring food to those who need it.')
  $('#item2').html('What We Do');
  $('#par2').html('In order to combat hunger, we\'ve developed a streamlined solution to help restaurants quickly and easily transport their leftovers to nearby homeless shelters in the area. Restaurant managers need only to take quick photos of any leftover food. Our app will then use cutting edge techniques in computer vision to recognize the food before automatically requesting delivery via Postmates. Once the delivery begins, customers can track where the food is in real time on our website.');
  $('#item3').html('The Next Steps');
  $('#par3').html('We\'d love to continue development of our app beyond this hackathon. Our long term goals include establishing a nonprofit organization and expanding our impact via grants and public funding.');
  $('#cred1').html('Created at HackMIT 2015');
  $('#cred2').html('');
}

function update() {
   $.ajax(
        {
            url: 'http://hackmit.joshcai.com/list_delivery',
            type: 'GET',
            processData: false
        }  
    ).then(
        function(json){

              //console.log(json);

                obj = JSON.parse(json);

                  // get positions & update markers here

  console.log('updating...');

  drivers.forEach(function(driver) {
    driver.setMap(null);
  });
  drivers = [];

  waiting.forEach(function(wait) {
    wait.setMap(null);
  });
  waiting = [];

  done.forEach(function(dun){
    dun.setMap(null);
  });
  done = [];

                for (var i=0; i<obj.data.length; i++) {

                  var delivery = obj.data[i];

                    var marker = new google.maps.Marker({
                      position: new google.maps.LatLng(delivery.pickup.location.lat, delivery.pickup.location.lng),
                      shelter: delivery.dropoff == null ? 'Unnamed Shelter' : delivery.dropoff.name,
                      courier: delivery.courier,
                      name: delivery.courier == null ? 'Anonymous Courier' : delivery.courier.name,
                      items: [],
                      description: delivery.manifest.description,

                      pickup_address: delivery.pickup == null ? 'Unknown address' : delivery.pickup.address,
                      pickup_city: delivery.pickup == null ? 'Unknown city' : delivery.pickup.detailed_address == null ? 'Unknown city' : delivery.pickup.detailed_address.city,
                      pickup_country: delivery.pickup == null ? 'Unknown country' : delivery.pickup.detailed_address == null ? 'Unknown country' : delivery.pickup.detailed_address.country,

                      destination: delivery.dropoff.location,
                      dest_address: delivery.dropoff == null ? 'Unknown address' : delivery.dropoff.address,
                      dest_city: delivery.dropoff == null ? 'Unknown city' : delivery.dropoff.detailed_address == null ? 'Unknown city' : delivery.dropoff.detailed_address.city,
                      dest_country: delivery.dropoff == null ? 'Unknown country' : delivery.dropoff.detailed_address == null ? 'Unknown country' : delivery.dropoff.detailed_address.country,

                      fee: delivery.fee*.01 - .01,

                      url: '/',
                      animation: google.maps.Animation.NONE
                    });

                  if (delivery.status === "pending") {
                    marker.setIcon('http://maps.google.com/mapfiles/ms/icons/red-dot.png');
                    marker.destination = new google.maps.LatLng(delivery.pickup.location.lat, delivery.pickup.location.lng);
                    waiting.push(marker);

                    marker.addListener('click', function(){

                                              var split = this.description.split(',');

                        $('#panel-title').html(this.shelter);
                        $('#item1').html(this.name);
                        $('#par1').html(this.courier == null ? "This anonymous courier has not left yet." : "<img class='courier-img' src='" + this.courier.img_href + "'><br>" + this.name + " has not left yet.");
                        $('#item2').html('Delivery Details');
                        $('#par2').html('Pickup address: ' + this.pickup_address + ', ' + this.pickup_city + ', ' + this.pickup_country + '<br>' + 'Destination address: ' + this.dest_address + ', ' + this.dest_city + ', ' + this.dest_country + '<br>Fee: $' + this.fee);
                        $('#item3').html('Delivery Description');
                        $('#par3').html(split.length < 2 ? this.description : "<img class='courier-img' src='" + split[0] + "'><br>" + split[1]);
                        $('#cred1').html('Delivered by ' + this.name);
                        $('#cred2').html('Donated to ' + this.shelter);
                      });
                  }

                  if (delivery.status === "pickup") {
                    marker.setIcon('http://maps.google.com/mapfiles/ms/icons/yellow-dot.png');
                    marker.destination = new google.maps.LatLng(delivery.pickup.location.lat, delivery.pickup.location.lng);
                    marker.position = delivery.courier == null ? null : new google.maps.LatLng(delivery.courier.location.lat, delivery.courier.location.lng);
                    drivers.push(marker)

                    marker.addListener('click', function(){

                                              var split = this.description.split(',');

                        $('#panel-title').html(this.shelter);
                        $('#item1').html(this.name);
                        $('#par1').html(this.courier == null ? "This anonymous courier is on the way for pickup." : "<img class='courier-img' src='" + this.courier.img_href + "'><br>" + this.name + " is on the way for pickup.");
                        $('#item2').html('Delivery Details');
                        $('#par2').html('Pickup address: ' + this.pickup_address + ', ' + this.pickup_city + ', ' + this.pickup_country + '<br>' + 'Destination address: ' + this.dest_address + ', ' + this.dest_city + ', ' + this.dest_country + '<br>Fee: $' + this.fee);
                        $('#item3').html('Delivery Description');
                        $('#par3').html(split.length < 2 ? this.description : "<img class='courier-img' src='" + split[0] + "'><br>" + split[1]);
                        $('#cred1').html('Delivered by ' + this.name);
                        $('#cred2').html('Donated to ' + this.shelter);

                        getRoute(this);
                      });
                  }

                  if (delivery.status === "pickup_complete" || delivery.status === "dropoff") {
                    marker.setIcon('http://maps.google.com/mapfiles/ms/icons/blue-dot.png');

                    if (marker.courier != null && marker.courier.img_href != null) {
                      var icon = {
                          url: marker.courier.img_href, // url
                          scaledSize: new google.maps.Size(32, 32), // scaled size
                          origin: new google.maps.Point(0,0), // origin
                          anchor: new google.maps.Point(0, 0) // anchor
                      };

                      marker.icon = icon;
                    }

                    marker.position = delivery.courier == null ? null : new google.maps.LatLng(delivery.courier.location.lat, delivery.courier.location.lng);
                    drivers.push(marker);

                    marker.addListener('click', function(){

                        var split = this.description.split(',');


                        $('#panel-title').html(this.shelter);
                        $('#item1').html(this.name);
                        $('#par1').html(this.courier == null ? "This anonymous courier has picked up these items." : "<img class='courier-img' src='" + this.courier.img_href + "'><br>" + this.name + "has picked up these items.");
                        $('#item2').html('Delivery Details');
                        $('#par2').html('Pickup address: ' + this.pickup_address + ', ' + this.pickup_city + ', ' + this.pickup_country + '<br>' + 'Destination address: ' + this.dest_address + ', ' + this.dest_city + ', ' + this.dest_country + '<br>Fee: $' + this.fee);
                        $('#item3').html('Delivery Description');
                        $('#par3').html(split.length < 2 ? this.description : "<img class='courier-img' src='" + split[0] + "'><br>" + split[1]);
                        $('#cred1').html('Delivered by ' + this.name);
                        $('#cred2').html('Donated to ' + this.shelter);

                        getRoute(this);
                      });
                  }

                  if (delivery.status === "delivered") {
                    marker.setIcon('http://maps.google.com/mapfiles/ms/icons/green-dot.png');
                    marker.position = new google.maps.LatLng(delivery.dropoff.location.lat, delivery.dropoff.location.lng);
                    done.push(marker);

                    marker.addListener('click', function(){

                        var split = this.description.split(',');

                        $('#panel-title').html(this.shelter);
                        $('#item1').html(this.name);
                        $('#par1').html(this.courier == null ? "This anonymous courier has finished delivering these items." : "<img class='courier-img' src='" + this.courier.img_href + "'><br>" + this.name + " delivered these items.");
                        $('#item2').html('Delivery Details');
                        $('#par2').html('Pickup address: ' + this.pickup_address + ', ' + this.pickup_city + ', ' + this.pickup_country + '<br>' + 'Destination address: ' + this.dest_address + ', ' + this.dest_city + ', ' + this.dest_country + '<br>Fee: $' + this.fee);
                        $('#item3').html('Delivery Description');
                        $('#par3').html(split.length < 2 ? this.description : "<img class='courier-img' src='" + split[0] + "'><br>" + split[1]);
                        $('#cred1').html('Delivered by ' + this.name);
                        $('#cred2').html('Donated to ' + this.shelter);

                        directionsDisplay.setDirections(null);
                      });
                  }
                }

                console.log('updating ' + waiting.length + ' ' + drivers.length + ' ' + done.length);


  for(var i=0; i<drivers.length; i++) {
    drivers[i].setMap(map);
  }

  for(var i=0; i<done.length; i++){
    done[i].setMap(map);
  }

  for(var i=0; i<waiting.length; i++){
    waiting[i].setMap(map);
  }

        }.bind(this),
        function(e){
          console.log('failed ' + e);
        }.bind(this)
    );

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