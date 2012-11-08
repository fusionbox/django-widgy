define([ 'widgy.contents',
    ], function(contents) {

  var BucketView = contents.ContentView.extend({
  });

  var Bucket = contents.Content.extend({
    viewClass: BucketView
  });

  return Bucket;
});
