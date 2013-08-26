var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert;

var WidgyBackbone = requirejs('widgy.backbone');

describe('Widgy ViewLists', function(){

  beforeEach(function(){
    test.create();

    this.MockView = function(cid){
      this.i_was_closed = false;
      this.off_was_called = false;
      this.on_was_called = true;
      this.cid = cid;
      this.on = function(){this.off_was_called = true;};
      this.off = function(){this.on_was_called = true;};
      this.close = function() { this.i_was_closed = true; };
      this.model = {
        id: cid
      };
    };

    this.view_list = new WidgyBackbone.ViewList();
  });

  afterEach(function(){
    test.destroy();
  });


  it('should push views onto the list property', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2);
    this.view_list.push(mockview);
    this.view_list.push(mockview1);
    assert.deepEqual(this.view_list.list, [ mockview, mockview1 ]);
  });


  it('should remove views by view object', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3);
    this.view_list.list = [ mockview, mockview1, mockview2 ];
    this.view_list.remove(mockview2);
    assert.deepEqual(this.view_list.list, [ mockview, mockview1 ]);
  });


  it('should return false if remove is called and view is not found', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3);
    this.view_list.list = [ mockview, mockview1 ];
    assert.isFalse(this.view_list.remove(mockview2));
  });


  it('should call close on each view in its list when closeAll is used', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3);
    this.view_list.list = [ mockview, mockview1, mockview2 ];
    this.view_list.closeAll();
    assert.isTrue(this.view_list.list[0].i_was_closed);
    assert.isTrue(this.view_list.list[1].i_was_closed);
    assert.isTrue(this.view_list.list[2].i_was_closed);
  });


  it('should find a view object from its model id', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3);
    this.view_list.list = [ mockview, mockview1, mockview2 ];
    assert.strictEqual(this.view_list.findById(2), mockview1);
  });


  it('should find a view object from its element', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3),
        search_el = document.createElement('div');
    search_el.setAttribute('id', 'found_me');
    mockview.el = document.createElement('div');
    mockview1.el = search_el;
    mockview2.el = document.createElement('div');

    this.view_list.list = [ mockview, mockview1, mockview2 ];
    assert.strictEqual(this.view_list.findByEl(search_el), mockview1);
  });

  it('should find a view object from its view model', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3);
    this.view_list.list = [ mockview, mockview1, mockview2 ];
    assert.strictEqual(this.view_list.findByModel(mockview1.model), mockview1);
  });

  it('should find return a view at a certain location', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3);
    this.view_list.list = [ mockview, mockview1, mockview2 ];
    assert.strictEqual(this.view_list.at(1), mockview1);
  });

  it('should find the index of a view', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3);
    this.view_list.list = [ mockview, mockview1, mockview2 ];
    assert.strictEqual(this.view_list.indexOf(mockview2), 2);
  });

  it('should test the setting of a ViewList', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3);
    this.view_list.set([ mockview, mockview1, mockview2 ]);
    assert.strictEqual(this.view_list.at(0), mockview);
    assert.strictEqual(this.view_list.at(1), mockview1);
    assert.strictEqual(this.view_list.at(2), mockview2);
    assert.isUndefined(this.view_list.at(3));
  });

  it('should find the number of items in ViewList', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3);
    this.view_list.list = [ mockview, mockview1, mockview2 ];
    assert.strictEqual(this.view_list.size(), 3);
  });

  it('should push a view into a certain index', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3);
    this.view_list.list = [ mockview, mockview2 ];
    this.view_list.push(mockview1, {at: 1});
    assert.strictEqual(this.view_list.at(0), mockview);
    assert.strictEqual(this.view_list.at(1), mockview1);
    assert.strictEqual(this.view_list.at(2), mockview2);
    assert.isUndefined(this.view_list.at(3));
  });
});

describe('Spinner View', function(){

  beforeEach(function(){
    test.create();
  });

  afterEach(function(){
    test.destroy();
  });

  it('should set the "disabled" property on its element on initialization', function(){
    var spinner = new WidgyBackbone.Spinner();
    assert.isTrue(spinner.el.disabled);
  });

  it('should unset the "disabled" property on its element after calling restore', function(){
    var spinner = new WidgyBackbone.Spinner();
    spinner.restore();
    assert.isFalse(spinner.el.disabled);
  });

  it('should add a "loading" class to its element on initialization', function(){
    var spinner = new WidgyBackbone.Spinner();
    assert.isTrue(spinner.$el.hasClass('loading'));
  });

  it('should remove "loading" class to its element on initialization', function(){
    var spinner = new WidgyBackbone.Spinner();
    spinner.restore();
    assert.isFalse(spinner.$el.hasClass('loading'));
  });

});
