

function submit_query(btn){

    var sitv = setInterval(function(){
        var prog_url = 'progressurl'                   // prog_url指请求进度的url，后面会在django中设置
        $.getJSON(prog_url, function(res){
            $('#prog_in').width(res + '%');     // 改变进度条进度，注意这里是内层的div， res是后台返回的进度
        });
    }, 1000);                                 // 每1秒查询一次后台进度

    thisurl = 'thisiurl'
    $.getJSON(thisurl, function(res){
        // ...
        clearInterval(sitv);                   // 此时请求成功返回结果了，结束对后台进度的查询
        $('#prog_in').width(100 + '%'); // 修改进度条外层div的class, 改为完成形态
        $('#pic1').attr("src",'static/images/network/modularity.png');
        $('#pic2').attr("src",'static/images/network/most_modularity.png');


    });

}