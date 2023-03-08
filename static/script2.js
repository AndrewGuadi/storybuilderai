

let page1Counter = 1;
const pageOne = document.getElementById('page1')
const pageTwo = document.getElementById('page2')



eventSource = new EventSource(`/stream?prompt=${text}`)


eventSource.addEventListener('message', (event) => {
    
    const data = event.data;
    if (page1Counter < 300){
      page1Counter ++;
      const newData = pageOne.lastElementChild || document.createElement('p');
      newData.textContent += data;
      if (!pageOne.lastElementChild) {
          pageOne.appendChild(newData);
        }
    }
    else{
      const newData = pageTwo.lastElementChild || document.createElement('p')
      newData.textContent += data
      if (!pageTwo.lastElementChild)
        pageTwo.appendChild(newData)
    }
  });

eventSource.addEventListener('error', (event) => {
    console.log('Error connecting to stream', event);
    eventSource.close();
    bookText = pageOne.textContent
    bookText += pageTwo.textContent
    prompt_text = `Create a SHORT Book Title for the following Text: ${bookText}`
    bookTitleEventSource = new EventSource(`/stream?prompt=${prompt_text}`)
    bookTitleEventSource.addEventListener("message", (event) =>{
      document.getElementById('book-title').innerHTML += event.data
    })
    bookTitleEventSource.addEventListener('error', (event) => {
      console.log('Error connecting to stream', event);
      bookTitleEventSource.close();
    })
    
    });
