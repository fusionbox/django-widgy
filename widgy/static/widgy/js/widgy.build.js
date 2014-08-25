({
    paths: {
        'jquery': './lib/jquery',
        'underscore': './lib/underscore',
        'backbone': './lib/backbone',
        'text': 'require/text',
    },
    skipDirOptimize: true,
    modules: [
        {
            name: 'widgy-main',
            // components get included dynamically, so they can't be detected.
            include: [
                'components/widget/component',
                'components/tabbed/component',
                'components/table/component',
                'components/tableheader/component',
            ],
        }
    ],
    map: {
      // http://requirejs.org/docs/jquery.html#noconflictmap
      '*': { 'jquery': 'jquery-private' },
      'jquery-private': { 'jquery': 'jquery' }
    }
})
