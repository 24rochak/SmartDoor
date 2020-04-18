var apigClient = apigClientFactory.newClient();

const url = new URL(window.location.href);
var faceID = url.searchParams.get("faceID");

function validateOTP(){
    let id = faceID;
    let pass = $('.passcode-input').val();
    console.log("faceID: ", id);
    console.log("passcode: ", pass);
    
    // POST 
    var params = {
    };
    var body = {
       "messages": [{
            "type": "string",
            "unstructured": {
                "id": 0,
                "faceID": id,
                "passcode": pass,
                "timestamp": "string"
            }
        }]
    };
    var additionalParams = {
    };

    return apigClient.validatePost(params, body, additionalParams)
        .then(function(result) {
            return result;
        }).catch(function(result) {
            return result;
        });
}

$('.passcode-submit').click(function(){
    
    validateOTP().then(function(return_data){
        let result = JSON.parse(return_data["data"]["body"])['result']
        console.log(result);
        if (result){
            alert("Successfully Login!");
        }
        else{
            alert("Your OTP code is incorrect");
        }
    })
    
})