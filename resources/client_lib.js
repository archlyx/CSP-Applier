var csp_client_lib = (function() {
  var page_url;
  var csp_build_external_js_url = "https://localhost:4433/js-factory";
  var csp_js_repository_url = "https://localhost:4433/allowed-resources/";
  var config = function(u, build_url, repo_url) {
    page_url = u;
    if (build_url) {
      csp_build_external_js_url = build_url;
    }
    if (repo_url) {
      csp_js_repository_url = repo_url;
    }
  }

  var csp_base64encode_script = function (script) {
    try{
      return btoa(script);
    }
    catch(e){
      console.log('failed to encode base64 script '+e);
      return null;
    }
  };

  var csp_create_script_node = function (src) {
    try{
      var script = document.createElement('script');
      script.src = src;
      return script;
    }
    catch (e) {
      console.log('erorr in csp_create_script_node '+ e)
    }
    return null;
  };

  var csp_replace_node = function (new_node, old_node) {
    try{
      var p_node = old_node.parentElement;
      if (p_node===null) {
        console.log("1 old node: "+old_node+" "+old_node.insert_before);
        //old_node.insert_before(new_node);
        document.getElementsByTagName('head')[0].appendChild(new_node);
      }
      else {
        console.log("2 old node: "+old_node+" "+old_node.insert_before);
         p_node.replaceChild(new_node, old_node);
      }
     
      console.log('done replacing node')
    }
    catch (e) {
      console.log('erorr in csp_replace_node '+ e)
    }
  };

  var csp_match_contents = function (script) {
    return script;
  };

  var csp_parse_url = function (url){
    var parser = document.createElement('a');
    parser.href = url;
    return parser.hostname;
  };

  var csp_rewrite_inline_script = function (old_script_node) {
    if (old_script_node.innerHTML === ""){
      return ;
    }
    var old_node  = old_script_node;
    var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
    var encoded_script = csp_base64encode_script(old_script_node.innerHTML);
    var file_name =  'dynamic_'+csp_parse_url(page_url) + '_' +Date.now()+'.js';
    var params = "file_name="+file_name+"&script=" + encoded_script;
    var new_node;

    var external_js_ready_callback = function () {
      if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
        try{
          var obj = JSON.parse(xmlhttp.responseText);
          if (obj.success === true) {
            console.log('successfully creating external JS\n');
            new_node = csp_create_script_node(csp_js_repository_url+file_name);
            csp_replace_node(new_node, old_node);
          }
          else {
            console.log('failed to create external js: '+obj.message);
          }
        }
        catch (e) {
          console.log('failed to create external js: '+obj.message);
        }
      }
    };

    xmlhttp.open("POST", csp_build_external_js_url, true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xmlhttp.onreadystatechange = external_js_ready_callback;
    xmlhttp.send(params);
  };

  var csp_observer = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      var node, node_name, script;
      for (var i = 0; i < mutation.addedNodes.length; i++){
        try{
          node = mutation.addedNodes[i];
          node_name = node.nodeName;
          if (node_name === "SCRIPT"){
            if (node.innerHTML === "") { continue; }
            script = csp_match_contents(node.innerHTML);
            if (script === "" ) { continue; }
            console.log("detect one added script node");
            csp_rewrite_inline_script(node);

          }
        }
        catch (e) {
          console.log("error in MutationObserver callback "+e);
        }
       
      }

    });
  });

  var cst_test_create_node = function () {
    var script = document.createElement('script');
    script.innerHTML = 
      "var xxx = 3; var yyy = 4; var z = xxx + yyy; alert('z value be '+z)";
    document.getElementsByTagName('head')[0].appendChild(script);
  };

  var csp_run_observer = function() {
    var csp_dom_observer_options = {
      subtree: true,
      childList: true,
      attributes: false
    };
    csp_observer.observe(document, csp_dom_observer_options);
  };

  return {
    config : config,
    run_observer : csp_run_observer,
    test : cst_test_create_node
  };

}) ();

csp_client_lib.config(document.URL);
csp_client_lib.run_observer();
