// --- Immediately invoked function for email.js ---
(function(){emailjs.init("user_qI0f2g6tNqj3cj8yeKtiz");})();


// --- Sends e-mail to my e-mail adress
function sendMail(contactForm) {
    emailjs.send("service_mncxtev", "contact", {
        "from_name": contactForm.name.value,
        "from_email": contactForm.emailaddress.value,
        "contact_request": contactForm.projectsummary.value
    })
    .then(
        function(response) {
            console.log("SUCCESS", response);
        },
        function(error) {
            console.log("FAILED", error);
        }
    );
    return false;  // To block from loading a new page
}
