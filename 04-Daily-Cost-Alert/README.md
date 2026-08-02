1) Here I developed a method check cost.

2) I got response from cost explorer API from 1st of month to current date

3) After that I checked if the cost recieved is greater than threshold amount (env variable)

4) If cost is greater I published a message to SNS

5) Why lambda over traditional AWS budget alert

a) We can define it categorywise which service used what
b) Better identification of reason why budget increased can be done
c) Traditional AWS alert has specific data. But in our lambda we can customize it
d) We can link multiple accounts for lambda
