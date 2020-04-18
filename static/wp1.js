
window.onload = function(){
    const url = new URL(window.location.href);
    const faceID = url.searchParams.get("faceID");
    source = "https://facedatabucketcca2.s3.amazonaws.com/faceImages/"+faceID+".jpg";
    photo = document.getElementById("photo")
    photo.src = source
}

var submitButton = document.getElementById("ApproveButton")
submitButton.onclick = function(){
    submitButton.disabled = true;
    rejectButton.disabled = true;
    var name = document.getElementById("name").value
    var phone = document.getElementById("phone-number").value

    if ( name.length==0 || phone.length==0){
        window.alert("Enter all details before submitting")
        submitButton.disabled = false;
        rejectButton.disabled = false;
        return
    }

    var val = +phone
    console.log(val)
    if (val==NaN || phone.length!=10){
        window.alert("Please enter a valid number")
        submitButton.disabled = false;
        rejectButton.disabled = false;
        return
    }

    const url = new URL(window.location.href);
    const faceID = url.searchParams.get("faceID");

    data = {'name':name, 'phoneNumber':val,'faceID':faceID, 'approve':true}
    console.log(data)
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            obj = JSON.parse(this.response);
            if (obj["statusCode"] == 200){
                window.alert("Successfully allowed the user")
            } else {
                window.alert("Some error occured.")
            }
        }
    };
    xhttp.open("POST", "https://53gvho4j9a.execute-api.us-east-1.amazonaws.com/final/face", false);
    xhttp.send(JSON.stringify(data));
};

var rejectButton = document.getElementById("RejectButton")
rejectButton.onclick = function(){
    submitButton.disabled = true;
    rejectButton.disabled = true;
    ans = window.confirm("Reject the user")
    if (ans) {
        window.alert("You have rejected the user.")
    } else {
        console.log("User clicked cancel")
        submitButton.disabled = false;
        rejectButton.disabled = false;
        return
    }
    return
};