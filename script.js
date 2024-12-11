document.getElementById('file-upload').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('original-image').innerHTML = `<img src="${e.target.result}" alt="Gambar Asli" style="max-width: 100%;">`;
        };
        reader.readAsDataURL(file);
    }
});

document.getElementById('transform-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const transformType = document.getElementById('transform-type').value;
    // Tambahkan logika untuk mengirim gambar dan transformasi ke server
    // dan menampilkan hasilnya di #transformed-image
});