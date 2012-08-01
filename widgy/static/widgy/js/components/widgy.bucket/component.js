define([ 'widgy.contents', 'text!components/bucket/bucket.html' ], function(contents, bucket_template) {

  var BucketView = contents.ContentView.extend({
    template: bucket_template
  });

  var Bucket = contents.Content.extend({
    viewClass: BucketView
  });

  return Bucket;
});
