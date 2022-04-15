(function() {
  var fn = function() {
    
    (function(root) {
      function now() {
        return new Date();
      }
    
      var force = false;
    
      if (typeof root._bokeh_onload_callbacks === "undefined" || force === true) {
        root._bokeh_onload_callbacks = [];
        root._bokeh_is_loading = undefined;
      }
    
      
      
    
      var element = document.getElementById("a873cfd4-a43d-401a-b22a-250e195e9846");
        if (element == null) {
          console.warn("Bokeh: autoload.js configured with elementid 'a873cfd4-a43d-401a-b22a-250e195e9846' but no matching script tag was found.")
        }
      
    
      function run_callbacks() {
        try {
          root._bokeh_onload_callbacks.forEach(function(callback) {
            if (callback != null)
              callback();
          });
        } finally {
          delete root._bokeh_onload_callbacks
        }
        console.debug("Bokeh: all callbacks have finished");
      }
    
      function load_libs(css_urls, js_urls, callback) {
        if (css_urls == null) css_urls = [];
        if (js_urls == null) js_urls = [];
    
        root._bokeh_onload_callbacks.push(callback);
        if (root._bokeh_is_loading > 0) {
          console.debug("Bokeh: BokehJS is being loaded, scheduling callback at", now());
          return null;
        }
        if (js_urls == null || js_urls.length === 0) {
          run_callbacks();
          return null;
        }
        console.debug("Bokeh: BokehJS not loaded, scheduling load and callback at", now());
        root._bokeh_is_loading = css_urls.length + js_urls.length;
    
        function on_load() {
          root._bokeh_is_loading--;
          if (root._bokeh_is_loading === 0) {
            console.debug("Bokeh: all BokehJS libraries/stylesheets loaded");
            run_callbacks()
          }
        }
    
        function on_error(url) {
          console.error("failed to load " + url);
        }
    
        for (let i = 0; i < css_urls.length; i++) {
          const url = css_urls[i];
          const element = document.createElement("link");
          element.onload = on_load;
          element.onerror = on_error.bind(null, url);
          element.rel = "stylesheet";
          element.type = "text/css";
          element.href = url;
          console.debug("Bokeh: injecting link tag for BokehJS stylesheet: ", url);
          document.body.appendChild(element);
        }
    
        const hashes = {"https://cdn.bokeh.org/bokeh/release/bokeh-2.3.3.min.js": "dM3QQsP+wXdHg42wTqW85BjZQdLNNIXqlPw/BgKoExPmTG7ZLML4EGqLMfqHT6ON", "https://cdn.bokeh.org/bokeh/release/bokeh-tables-2.3.3.min.js": "8x57I4YuIfu8XyZfFo0XVr2WAT8EK4rh/uDe3wF7YuW2FNUSNEpJbsPaB1nJ2fz2", "https://cdn.bokeh.org/bokeh/release/bokeh-widgets-2.3.3.min.js": "3QTqdz9LyAm2i0sG5XTePsHec3UHWwVsrOL68SYRoAXsafvfAyqtQ+h440+qIBhS"};
    
        for (let i = 0; i < js_urls.length; i++) {
          const url = js_urls[i];
          const element = document.createElement('script');
          element.onload = on_load;
          element.onerror = on_error.bind(null, url);
          element.async = false;
          element.src = url;
          if (url in hashes) {
            element.crossOrigin = "anonymous";
            element.integrity = "sha384-" + hashes[url];
          }
          console.debug("Bokeh: injecting script tag for BokehJS library: ", url);
          document.head.appendChild(element);
        }
      };
    
      function inject_raw_css(css) {
        const element = document.createElement("style");
        element.appendChild(document.createTextNode(css));
        document.body.appendChild(element);
      }
    
      
      var js_urls = ["https://cdn.bokeh.org/bokeh/release/bokeh-2.3.3.min.js", "https://cdn.bokeh.org/bokeh/release/bokeh-widgets-2.3.3.min.js", "https://cdn.bokeh.org/bokeh/release/bokeh-tables-2.3.3.min.js"];
      var css_urls = [];
      
    
      var inline_js = [
        function(Bokeh) {
          Bokeh.set_log_level("info");
        },
        
        function(Bokeh) {
          (function() {
            var fn = function() {
              Bokeh.safely(function() {
                (function(root) {
                  function embed_document(root) {
                    
                  var docs_json = '{"bf927d3d-64f3-486b-a3bc-e28540d6062e":{"defs":[],"roots":{"references":[{"attributes":{},"id":"1009","type":"LinearScale"},{"attributes":{},"id":"1020","type":"WheelZoomTool"},{"attributes":{},"id":"1012","type":"BasicTicker"},{"attributes":{},"id":"1005","type":"DataRange1d"},{"attributes":{},"id":"1019","type":"PanTool"},{"attributes":{"overlay":{"id":"1025"}},"id":"1021","type":"BoxZoomTool"},{"attributes":{},"id":"1049","type":"UnionRenderers"},{"attributes":{},"id":"1022","type":"SaveTool"},{"attributes":{"formatter":{"id":"1044"},"major_label_policy":{"id":"1042"},"ticker":{"id":"1016"}},"id":"1015","type":"LinearAxis"},{"attributes":{"data_source":{"id":"1033"},"glyph":{"id":"1034"},"hover_glyph":null,"muted_glyph":null,"nonselection_glyph":{"id":"1035"},"view":{"id":"1037"}},"id":"1036","type":"GlyphRenderer"},{"attributes":{},"id":"1023","type":"ResetTool"},{"attributes":{},"id":"1007","type":"LinearScale"},{"attributes":{},"id":"1003","type":"DataRange1d"},{"attributes":{},"id":"1045","type":"AllLabels"},{"attributes":{"source":{"id":"1033"}},"id":"1037","type":"CDSView"},{"attributes":{},"id":"1047","type":"BasicTickFormatter"},{"attributes":{"formatter":{"id":"1047"},"major_label_policy":{"id":"1045"},"ticker":{"id":"1012"}},"id":"1011","type":"LinearAxis"},{"attributes":{"fill_color":{"value":"#1f77b4"},"line_color":{"value":"#1f77b4"},"x":{"field":"x"},"y":{"field":"y"}},"id":"1034","type":"Circle"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"x":{"field":"x"},"y":{"field":"y"}},"id":"1035","type":"Circle"},{"attributes":{},"id":"1050","type":"Selection"},{"attributes":{},"id":"1041","type":"Title"},{"attributes":{"below":[{"id":"1011"}],"center":[{"id":"1014"},{"id":"1018"}],"left":[{"id":"1015"}],"renderers":[{"id":"1036"}],"title":{"id":"1041"},"toolbar":{"id":"1026"},"x_range":{"id":"1003"},"x_scale":{"id":"1007"},"y_range":{"id":"1005"},"y_scale":{"id":"1009"}},"id":"1002","subtype":"Figure","type":"Plot"},{"attributes":{},"id":"1024","type":"HelpTool"},{"attributes":{"axis":{"id":"1011"},"ticker":null},"id":"1014","type":"Grid"},{"attributes":{},"id":"1044","type":"BasicTickFormatter"},{"attributes":{},"id":"1042","type":"AllLabels"},{"attributes":{"bottom_units":"screen","fill_alpha":0.5,"fill_color":"lightgrey","left_units":"screen","level":"overlay","line_alpha":1.0,"line_color":"black","line_dash":[4,4],"line_width":2,"right_units":"screen","syncable":false,"top_units":"screen"},"id":"1025","type":"BoxAnnotation"},{"attributes":{"active_multi":null,"tools":[{"id":"1019"},{"id":"1020"},{"id":"1021"},{"id":"1022"},{"id":"1023"},{"id":"1024"}]},"id":"1026","type":"Toolbar"},{"attributes":{"axis":{"id":"1015"},"dimension":1,"ticker":null},"id":"1018","type":"Grid"},{"attributes":{"data":{"x":[1,2],"y":[3,4]},"selected":{"id":"1050"},"selection_policy":{"id":"1049"}},"id":"1033","type":"ColumnDataSource"},{"attributes":{},"id":"1016","type":"BasicTicker"}],"root_ids":["1002"]},"title":"Bokeh Application","version":"2.3.3"}}';
                  var render_items = [{"docid":"bf927d3d-64f3-486b-a3bc-e28540d6062e","root_ids":["1002"],"roots":{"1002":"a873cfd4-a43d-401a-b22a-250e195e9846"}}];
                  root.Bokeh.embed.embed_items(docs_json, render_items);
                
                  }
                  if (root.Bokeh !== undefined) {
                    embed_document(root);
                  } else {
                    var attempts = 0;
                    var timer = setInterval(function(root) {
                      if (root.Bokeh !== undefined) {
                        clearInterval(timer);
                        embed_document(root);
                      } else {
                        attempts++;
                        if (attempts > 100) {
                          clearInterval(timer);
                          console.log("Bokeh: ERROR: Unable to run BokehJS code because BokehJS library is missing");
                        }
                      }
                    }, 10, root)
                  }
                })(window);
              });
            };
            if (document.readyState != "loading") fn();
            else document.addEventListener("DOMContentLoaded", fn);
          })();
        },
        function(Bokeh) {
        
        
        }
      ];
    
      function run_inline_js() {
        
        for (var i = 0; i < inline_js.length; i++) {
          inline_js[i].call(root, root.Bokeh);
        }
        
      }
    
      if (root._bokeh_is_loading === 0) {
        console.debug("Bokeh: BokehJS loaded, going straight to plotting");
        run_inline_js();
      } else {
        load_libs(css_urls, js_urls, function() {
          console.debug("Bokeh: BokehJS plotting callback run at", now());
          run_inline_js();
        });
      }
    }(window));
  };
  if (document.readyState != "loading") fn();
  else document.addEventListener("DOMContentLoaded", fn);
})();