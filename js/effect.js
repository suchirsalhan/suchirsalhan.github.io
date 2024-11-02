document.body.onmousemove = e => {
  for(const elem of document.getElementsByClassName("card-base")) {
    const rect = elem.getBoundingClientRect(),
          x = e.clientX - rect.left,
          y = e.clientY - rect.top;

    elem.style.setProperty("--mouse-x", `${x}px`);
    elem.style.setProperty("--mouse-y", `${y}px`);
  };
}
