define(['jquery'], function($) {
    /*! fixto - v0.1.7 - 2013-02-02
    * http://github.com/bbarakaci/fixto/*/
	// Start Computed Style. Please do not modify this module here. Modify it from its own repo. See address below.

    /*! Computed Style - v0.1.0 - 2012-07-19
    * https://github.com/bbarakaci/computed-style
    * Copyright (c) 2012 Burak Barakaci; Licensed MIT */
    var computedStyle = (function() {
        var computedStyle = {
            getAll : function(element){
                return document.defaultView.getComputedStyle(element);
            },
            get : function(element, name){
                return this.getAll(element)[name];
            },
            toFloat : function(value){
                return parseFloat(value, 10) || 0;
            },
            getFloat : function(element,name){
                return this.toFloat(this.get(element, name));
            },
            _getAllCurrentStyle : function(element) {
                return element.currentStyle;
            }
        };

        if (document.documentElement.currentStyle) {
            computedStyle.getAll = computedStyle._getAllCurrentStyle;
        }

        return computedStyle;

    }());

	// End Computed Style. Modify whatever you want to.

    var mimicNode = (function(){
        /*
        Class Mimic Node
        Dependency : Computed Style
        Tries to mimick a dom node taking his styles, dimensions. May go to his repo if gets mature.
        */

        function MimicNode(element) {
            this.element = element;
            this.replacer = document.createElement('div');
            this.replacer.style.visibility = 'hidden';
            this.hide();
            element.parentNode.insertBefore(this.replacer, element);
        }

        MimicNode.prototype = {
            replace : function(){
                var rst = this.replacer.style;
                var styles = computedStyle.getAll(this.element);

                 // rst.width = computedStyle.width(this.element) + 'px';
                 // rst.height = this.element.offsetHeight + 'px';

                 // Setting offsetWidth
                 rst.width = this._width();
                 rst.height = this._height();

                 // Adobt margins
                 rst.marginTop = styles.marginTop;
                 rst.marginBottom = styles.marginBottom;
                 rst.marginLeft = styles.marginLeft;
                 rst.marginRight = styles.marginRight;

                 // Adopt positioning
                 rst.cssFloat = styles.cssFloat;
                 rst.styleFloat = styles.styleFloat; //ie8;
                 rst.position = styles.position;
                 rst.top = styles.top;
                 rst.right = styles.right;
                 rst.bottom = styles.bottom;
                 rst.left = styles.left;
                 // rst.borderStyle = styles.borderStyle;

                 rst.display = styles.display;

            },

            hide: function () {
                this.replacer.style.display = 'none';
            },

            _width : function(){
                return this.element.getBoundingClientRect().width + 'px';
            },

            _widthOffset : function(){
                return this.element.offsetWidth + 'px';
            },

            _height : function(){
                return this.element.getBoundingClientRect().height + 'px';
            },

            _heightOffset : function(){
                return this.element.offsetHeight + 'px';
            },

            destroy: function () {
                $(this.replacer).remove();

                // set properties to null to break references
                for (var prop in this) {
                    if (this.hasOwnProperty(prop)) {
                      this[prop] = null;
                    }
                }
            }
        };

        var bcr = document.documentElement.getBoundingClientRect();
        if(!bcr.width){
            MimicNode.prototype._width = MimicNode.prototype._widthOffset;
            MimicNode.prototype._height = MimicNode.prototype._heightOffset;
        }

        return {
            MimicNode:MimicNode,
            computedStyle:computedStyle
        };
    }());

    // Dirty business
    var ie = window.navigator.appName === 'Microsoft Internet Explorer';
    var ieversion;

    if(ie){
        ieversion = parseFloat(window.navigator.appVersion.split("MSIE")[1]);
    }

    // Class FixToContainer

    function FixToContainer(child, parent, options) {
        this.child = child;
        this._$child = $(child);
        this.parent = parent;
        this._replacer = new mimicNode.MimicNode(child);
        this._ghostNode = this._replacer.replacer;
        this.options = $.extend({
            className: 'fixto-fixed'
        }, options);
        if(this.options.mind) {
            this._$mind = $(this.options.mind);
        }
        if(this.options.zIndex) {
            this.child.style.zIndex = this.options.zIndex;
        }

        this._saveStyles();

        this._saveViewportHeight();

        // Create anonymous functions and keep references to register and unregister events.
        this._proxied_onscroll = this._bind(this._onscroll, this);
        this._proxied_onresize = this._bind(this._onresize, this);



        this.start();
    }

    FixToContainer.prototype = {

        // Returns an anonymous function that will call the given function in the given context
        _bind : function (fn, context) {
            return function () {
                return fn.call(context);
            };
        },

        // at ie8 maybe only in vm window resize event fires everytime an element is resized.
        _toresize : ieversion===8 ? document.documentElement : window,

        // Returns the total outerHeight of the elements passed to mind option. Will return 0 if none.
        _mindtop: function () {
            var top = 0;
            if(this._$mind) {
                $(this._$mind).each(function () {
                    top += $(this).outerHeight(true);
                });
            }
            return top;
        },

        _onscroll: function _onscroll() {
            this._scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
            this._parentBottom = (this.parent.offsetHeight + this._fullOffset('offsetTop', this.parent)) - computedStyle.getFloat(this.parent, 'paddingBottom');
            if (!this.fixed) {
                if (
                    this._scrollTop < this._parentBottom &&
                    this._scrollTop > (this._fullOffset('offsetTop', this.child) - computedStyle.getFloat(this.child, 'marginTop') - this._mindtop()) &&
                    this._viewportHeight > (this.child.offsetHeight + computedStyle.getFloat(this.child, 'marginTop') + computedStyle.getFloat(this.child, 'marginBottom'))
                ) {
                    this._fix();
                    this._adjust();
                }
            } else {
                if (this._scrollTop > this._parentBottom || this._scrollTop < (this._fullOffset('offsetTop', this._ghostNode) - computedStyle.getFloat(this._ghostNode, 'marginTop') - this._mindtop())) {
                    this._unfix();
                    return;
                }
                this._adjust();
            }
        },

        _adjust: function _adjust() {
            var diff = (this._parentBottom - this._scrollTop) - (this.child.offsetHeight + computedStyle.getFloat(this.child, 'marginTop') + computedStyle.getFloat(this.child, 'marginBottom') + this._mindtop());
            var mindTop = this._mindtop();
            if (diff < 0) {
                this.child.style.top = (diff + mindTop) + 'px';
            }
            else {
                this.child.style.top = (0 + mindTop) + 'px';
            }
        },

        /*
        I need some performance on calculating offset as it is called a lot of times.
        This function calculates cumulative offsetTop way faster than jQuery $.offset
        todo: check vs getBoundingClientRect
        */

        _fullOffset: function _fullOffset(offsetName, elm) {
            var offset = elm[offsetName];
            while (elm.offsetParent !== null) {
                elm = elm.offsetParent;
                offset = offset + elm[offsetName];
            }
            return offset;
        },

        _fix: function _fix() {
            var child = this.child,
                childStyle = child.style;
            this._saveStyles();

            if(document.documentElement.currentStyle){
                var styles = computedStyle.getAll(child);
                childStyle.left = (this._fullOffset('offsetLeft', child) - computedStyle.getFloat(child, 'marginLeft')) + 'px';
                // Function for ie<9. when hasLayout is not triggered in ie7, he will report currentStyle as auto, clientWidth as 0. Thus using offsetWidth.
                childStyle.width = (child.offsetWidth) - (computedStyle.toFloat(styles.paddingLeft) + computedStyle.toFloat(styles.paddingRight) + computedStyle.toFloat(styles.borderLeftWidth) + computedStyle.toFloat(styles.borderRightWidth)) + 'px';
            }
            else {
                childStyle.width = computedStyle.get(child, 'width');
                childStyle.left = (child.getBoundingClientRect().left - computedStyle.getFloat(child, 'marginLeft')) + 'px';
            }

            this._replacer.replace();
            childStyle.position = 'fixed';
            childStyle.top = this._mindtop() + 'px';
            this._$child.addClass(this.options.className);
            this.fixed = true;
        },

        _unfix: function _unfix() {
            var childStyle = this.child.style;
            this._replacer.hide();
            childStyle.position = this._childOriginalPosition;
            childStyle.top = this._childOriginalTop;
            childStyle.width = this._childOriginalWidth;
            childStyle.left = this._childOriginalLeft;
            this._$child.removeClass(this.options.className);
            this.fixed = false;
        },

        _saveStyles: function(){
            var childStyle = this.child.style;
            this._childOriginalPosition = childStyle.position;
            this._childOriginalTop = childStyle.top;
            this._childOriginalWidth = childStyle.width;
            this._childOriginalLeft = childStyle.left;
        },

        _onresize: function () {
            this._saveViewportHeight();
            this._unfix();
            this._onscroll();
        },

        _saveViewportHeight: function () {
            // ie8 doesn't support innerHeight
            this._viewportHeight = window.innerHeight || document.documentElement.clientHeight;
        },

        // Public method to stop the behaviour of this instance.
        stop: function () {

            // Unfix the container immediately.
            this._unfix();

            // remove event listeners
            $(window).unbind('scroll', this._proxied_onscroll);
            $(this._toresize).unbind('resize', this._proxied_onresize);

            this._running = false;
        },

        // Public method starts the behaviour of this instance.
        start: function () {

            // Start only if it is not running not to attach event listeners multiple times.
            if(!this._running) {

                // Trigger onscroll to have the effect immediately.
                this._onscroll();

                // Attach event listeners
                $(window).bind('scroll', this._proxied_onscroll);
                $(this._toresize).bind('resize', this._proxied_onresize);

                this._running = true;
            }
        },

        //Public method to destroy fixto behaviour
        destroy: function () {
            this.stop();

            // Remove jquery data from the element
            this._$child.removeData('fixto-instance');

            // Destroy mimic node instance
            this._replacer.destroy();

            // set properties to null to break references
            for (var prop in this) {
                if (this.hasOwnProperty(prop)) {
                  this[prop] = null;
                }
            }
        }

    };

    var fixTo = function fixTo(childElement, parentElement, options) {
        return new FixToContainer(childElement, parentElement, options);
    };

    /*
    No support for touch devices and ie lt 8
    */
    var touch = !!('ontouchstart' in window);

    if(touch || ieversion<8){
        fixTo = function(){
            return 'not supported';
        };
    }

    // Let it be a jQuery Plugin
    $.fn.fixTo = function (targetSelector, options) {

         var $targets = $(targetSelector);

         var i = 0;
         return this.each(function () {

             // Check the data of the element.
             var instance = $(this).data('fixto-instance');

             // If the element is not bound to an instance, create the instance and save it to elements data.
             if(!instance) {
                 $(this).data('fixto-instance', fixTo(this, $targets[i], options));
             }
             else {
                 // If we already have the instance here, expect that targetSelector parameter will be a string
                 // equal to a public methods name. Run the method on the instance without checking if
                 // it exists or it is a public method or not. Cause nasty errors when necessary.
                 var method = targetSelector;
                 instance[method].call(instance);
             }
             i++;
          });
    };

    /*
        Expose
    */

    return {
        FixToContainer: FixToContainer,
        fixTo: fixTo,
        computedStyle:computedStyle,
        mimicNode:mimicNode
    };
});
