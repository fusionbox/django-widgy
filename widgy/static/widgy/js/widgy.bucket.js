;(function(Widgy) {


  var BucketView = Widgy.contents.ContentView.extend({
    template: 'bucket'
  });

  var Bucket = Widgy.contents.Content.extend({
    viewClass: BucketView
  });


  Widgy.contents.registerModel('Bucket', Bucket);

})(this.Widgy);
