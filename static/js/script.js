$(function(){
  
  $('body').on("submit", ".like-button", likeCafe);
  $('body').on("submit", ".unlike-button", unlikeCafe);
});

async function likeCafe(e){
  e.preventDefault()
  $parent = $(e.target).parent();
  cafe_id = $parent.attr('id').split('-')[2];
   
  await axios.post('/api/like', {"cafe_id": cafe_id});
  
  
  $parent.empty()
  $parent.append(`
    <form class="d-inline-block unlike-button" method="POST" action="/api/unlike">
      <button class="btn btn-outline-primary mb-3" id="like-button">Unlike</button>
    </form>
  `)

}


async function unlikeCafe(e){
  e.preventDefault()

  $parent = $(e.target).parent();
  cafe_id = $parent.data('id').split('-')[2];
  /* TODO can use data attributes (e.g. data-cafe-id={{ cafe.id }})*/

  await axios.post('/api/unlike', {"cafe_id": cafe_id});

  // TODO refactor to just change individual attributes
  $parent.empty()
  $parent.append(`
    <form class="d-inline-block like-button" method="POST" action="/api/like">
      <button class="btn btn-outline-primary mb-3" id="like-button">Like</button>
    </form>
  `)
}