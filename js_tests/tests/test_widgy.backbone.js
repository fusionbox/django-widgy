var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert;

var WidgyBackbone = requirejs('widgy.backbone'),
    nodes = requirejs('nodes/nodes'),
    $ = requirejs('jquery'),
    Q = requirejs('lib/q');

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

describe('View.close()', function(){
  beforeEach(function(){
    this.view_list = new WidgyBackbone.ViewList();
    this.view_to_close = new WidgyBackbone.View();
    this.view_list.push(this.view_to_close);
  });

  it('has a function to close', function(){
    assert.strictEqual(this.view_list.at(0), this.view_to_close);
    this.view_to_close.close();
    assert.isUndefined(this.view_list.at(0));
  });

  it('checks if event.preventDefault is true on close', function(){
    var event = new $.Event();
    assert.isFalse(event.isDefaultPrevented());
    this.view_to_close.close(event);
    assert.isTrue(event.isDefaultPrevented());
  });

  it('checks if event.preventDefault is true on close - negative', function() {
    var event = new $.Event();
    assert.isFalse(event.isDefaultPrevented());
    event.preventDefault = false;
    this.view_to_close.close(event);
    assert.isFalse(event.isDefaultPrevented());
  });
});

describe('View template and render', function(){
  beforeEach(function(){
    this.node = new nodes.Node({
      title: 'test',
      content:
        {component: 'testcomponent'}
    });
    this.view = new WidgyBackbone.View({model: this.node});
    this.view.template = '<span><%title%></span>';
  });

  it('gets Template and returns it', function(){
    assert.strictEqual(this.view.getTemplate(), this.view.template);
  });

  it('returns false if no template', function(){
    this.view.template = false;
    assert.isFalse(this.view.getTemplate());
  });

  it('should return a rendered template from Mustache', function(){
    assert.strictEqual(WidgyBackbone.renderTemplate('<%title%>',
      {title: 'test'}), 'test');
  });

  it('should render a template with render', function(){
    this.view.render();
    assert.strictEqual(this.view.$el.html(), '<span>test</span>');
  });

  it('should render a template with renderHTML', function(){
    this.view.renderHTML(this.view.getTemplate());
    assert.strictEqual(this.view.$el.html(), '<span>test</span>');
  });

  it('should render a promise with renderPromise', function(){
    var promise = this.view.renderPromise()
    promise.then(function(temp) {
      assert.strictEqual(temp.$el.html(), '<span>test</span>')
    })
    .done();
  });
});

describe('Model', function(){
  it('should return a url', function(){
    var mdl = new WidgyBackbone.Model();
    mdl.id = undefined;
    mdl.urlRoot = 1;
    assert.strictEqual(mdl.url(), 1);
  });

  it('should return and ID', function(){
    var mdl = new WidgyBackbone.Model();
    mdl.id = 1;
    assert.strictEqual(mdl.url(), 1);
  });
});
