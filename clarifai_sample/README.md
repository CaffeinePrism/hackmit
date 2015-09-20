# clarifai-HackMIT

## Welcome Hackers!

We are thrilled to offer you early access to the Clarifai Custom Model Training APIs. These APIs have never been used outside of our walls so we can't wait to see what awesome hacks are built on top of them. 

> Note: in addition to this brand-new custom training support, we also offer a suite of visual recognition and tagging APIs. You can find more information at our [developer site](https://developer.clarifai.com/docs/). Additional resources, including clients in a variety of languages, can be found on our [Github page](https://github.com/Clarifai).

## Signup

Before you begin, please make sure to signup at the special  [HackMIT 2015 Clarifai Signup Page](https://developer-alpha.clarifai.com/signup/HackMIT). This will give you free access to our alpha API. 

## Introduction To Custom Training

The Clarifai Deep Learning Platform recognizes concepts within images. These concepts may be objects, things or even emotions. While the platform recognizes an ever-growing number of concepts, there may be times when you would like to create your own concepts and train the platform to recognize those. We call this Custom Training. 

## A Quick Warning!

This API and functionality is experimental and alpha at best. Please email us at hackmit@clarifai.com and let us know what's not working how you'd expect it to work. We want to make this awesome. Please help us do that!

**Please note:** The API endpoint for Custom Training is https://api**-alpha**.clarifai.com. It's important to use this and not our production endpoint. 

## Prerequisites

This guide assumes that you have:

1. Created a developer account at https://developer-alpha.clarifai.com/signup/HackMIT
2. Created an Application https://developer-alpha.clarifai.com/docs/applications
3. Generated an Access Token from your Application page

## Getting Started

Custom Training allows you to create your own **Concepts** and then use the Clarifai Deep Learning platform to make **Predictions** based on those concepts. 

The basic workflow to create a custom **Concept** is:

1. Add some images that are **Positive** examples of a specific concept.
2. Add some images that are **Negative** examples for the same concept. That is, negative examples for 'car' are images that do not show a car.
3. Explicitly tell the platform to **Train** on those images.
4. Send a new image and ask the platform to **Predict** whether is contains your custom concept or not.

## Examples

A Javascript example is shown in the next section. There's a Python example below.

### Javascript

Include our JS library in your HTML doc:

```html
<script type="text/javascript" src="clarifai-basic.js"></script>
```

Be sure to also include jQuery:

```html
<script type="text/javascript" src="http://code.jquery.com/jquery-2.1.4.min.js"></script>
```

On document ready, instantiate the Clarifai object with your access token:

```js
$(document).ready(
  function(){
      var clarifai = new Clarifai({{ YOUR_ACCESS_TOKEN }});
  }  
);
```

Provide some **Positive** images for your custom **Concept**:

```js
clarifai.positive('http://example.com/image.jpg', 'car', callback);
```

Provide some **Negative** images for your custom **Concept**:

```js
clarifai.negative('http://example.com/another-image.jpg', 'car', callback);
```

After providing a few **Positives** and **Negative**, **Train** the platform with your **Concept**:

```js
clarifai.train('car', callback);
```

Now send some images and **Predict** whether they contain your custom **Concept**:

```js
clarifai.predict('http://example.com/some-new-image.jpg', 'car', callback);
```

You will receive a **Prediction** response:

```js
{
  "url": "http://example.com/some-new-image.jpg",
  "score": 0.9852
}
```
Putting it all together:

```js
// instantiate a new Clarifai object
var clarifai = new Clarifai(
  {
    'accessToken': YOUR_ACCESS_TOKEN
  }
);

// Give a few positive examples and a name for the custom concept.
clarifai.positive('http://example.com/car.jpg', 'car');

// Give a few negative examples and a name for the custom concept.
clarifai.negative('http://example.com/not-a-car.jpg', 'car');

// Train the platform on your custom concept.
clarifai.train('car');

// Ask for a prediction on a new image with your custom concept.
clarifai.predict('http://example.com/a-new-car.jpg', 'car');
```

By the way, all the function calls return promises and also take callbacks as their last argument.

Promise:

```js
clarifai.predict('http://example.com/a-new-car.jpg', 'car').then(
  function(obj){
    // the results of your predict call
  },
  function(e){
    // an error occurred
  }
);
```

Callback:

```js
clarifai.predict('http://example.com/a-new-car.jpg', 'car', function(obj){
  // success or error
});
```

### Python

#### Setup

To use the Python custom training api and run the example, you need to first
install the Clarifai API Python client. You don't need to get an Access Token
from the developer site, the API will retrieve one for you as long as you set
your environment variables.

<pre>
pip install git+git://github.com/Clarifai/Clarifai_py.git
export CLARIFAI_APP_ID=&lt;an_application_id_from_your_account&gt;
export CLARIFAI_APP_SECRET=&lt;an_application_secret_from_your_account&gt;
</pre>

Next, get the Clarifai Custom Model API and example script `example.py`.

<pre>
git clone git@github.com:Clarifai/clarifai-HackMIT
cd clarifai-HackMIT
</pre>

#### Run example.py

If everything is set up properly, you'll see the following output. We'll explain what's going on next.

<pre>
Success 0.797 http://phishthoughts.com/wp-content/uploads/2012/07/photo-1-11-e1342391144673.jpg
Success 0.706 http://bobmarley.cdn.junip.com/wp-content/uploads/2014/10/DSC01226-e1311293061704.jpg
Success 0.356 http://farm3.static.flickr.com/2161/2141620332_2b741028b3.jpg
Success 0.273 http://www.mediaspin.com/joel/grateful_dead230582_15-52.jpg
</pre>

Instantiate a ClarifaiCustomModel object. This is your custom **Concept**:

```python
from clarifai_basic import ClarifaiCustomModel
concept = ClarifaiCustomModel()
```

Provide some **Positive** example images for your custom **Concept**:

```python
concept.positive('http://example.com/car.jpg', 'car' );
```

Provide some **Negative** example images for your custom **Concept**:

```python
concept.negative('http://example.com/not-a-car.jpg', 'car' );
```

After providing a few **Positive** examples and a few **Negative** examples, **Train** the platform with your **Concept**:

```python
concept.train('car');
```

Now send some images and **Predict** whether they contain your custom **Concept**:

```python
result = concept.predict('http://example.com/maybe-a-car.jpg', 'car');
```

You will receive a **Prediction** response:

```json
{ "status": {
    "status": "OK", 
    "message": "Success"
    }, 
  "urls": [{
    "url": "http://example.com/maybe-a-car.jpg", 
    "score": 0.7794588208198547}]
}
```
The example script shows how to easily get the url and confidence score.

Putting it all together:

```python
#instantiate a new Clarifai object
from clarifai_basic import ClarifaiCustomModel
clarifai = ClarifaiCustomModel()

# Give a few positive examples and a name for the custom concept.
clarifai.positive('http://example.com/car.jpg', 'car');

# Give a few negative examples and a name for the custom concept.
clarifai.negative('http://example.com/not-a-car.jpg', 'car');

# Train the platform to learn your custom concept.
clarifai.train('car');

# Ask for a prediction on a new image with your custom concept.
result = clarifai.predict('http://example.com/a-new-car.jpg', 'car');

# Get the confidence that this image is a car.
confidence = result['urls'][0]['score']
```

Remember, the more **Positive** and **Negative** images you supply, the better the platform will get at making **Predictions**.


## Help

If you need anything at all, please email us (hackmit@clarifai.com), Tweet at us [@clarifaidev](https://twitter.com/clarifaidev) or find one of us at the hackathon (we sent a squad!).

Have fun and good luck!

