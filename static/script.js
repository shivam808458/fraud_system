document.addEventListener("DOMContentLoaded",()=>{

let form=document.getElementById("fraudForm")

if(form){
form.onsubmit=async(e)=>{
e.preventDefault()

let features=[
amount.value,
v1.value,
v2.value,
v3.value
]

let res=await fetch("/predict",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({features})
})

let data=await res.json()
result.innerText="Result: "+data.result
}
}

})