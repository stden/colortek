var deg2rad = function(deg){
    return deg * (Math.PI/180);
}
var l2distance = function(src, dst){
    math = Math;
    radius = 6371 //killometers
    
    dlat = deg2rad(dst.lat - src.lat);
    dlng = deg2rad(dst.lng - src.lng);
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(deg2rad(src.lat)) *
        math.cos(deg2rad(dst.lat)) * math.sin(dlng/2) * math.sin(dlng/2);
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a));
    d = radius * c;
    return d * 1000; //meters
}
