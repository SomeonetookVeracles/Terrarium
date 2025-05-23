//This is the main javascript file for the electron stuff
//It includes the positioning of the window, the scaling,
//And activating the HTML files through index.html

const { app, BrowserWindow, Tray, Menu, screen } = require('electron');
const path = require('path');
const readline = require('readline'); // ✅ Correct lowercase variable

let win;
let tray;

function createWindow() { //  Includes togglewindow and browserwindow functions
  const display = screen.getPrimaryDisplay();
  const { width: screenWidth, height: screenHeight } = display.workAreaSize;

  const widthpercent = 0.20;  //VAR - 15% width
  const heightpercent = 0.50; //VAR - 20% height

  //Multiplies screen size (pixels) by percentage
  const windowWidth = Math.floor(screenWidth * widthpercent);
  const windowHeight = Math.floor(screenHeight * heightpercent);

  // Defensive: make sure the sizes are numbers
  if (isNaN(windowWidth) || isNaN(windowHeight)) {
    throw new Error('Window dimensions are invalid.');
  }

  win = new BrowserWindow({
    width: windowWidth,
    height: windowHeight,
    frame: false,
    transparent: false,
    alwaysOnTop: true,
    resizable: false,
    skipTaskbar: true,
    show: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // Position in bottom-right corner, with extra safety
  const posX = Math.max(0, screenWidth - windowWidth);
  const posY = Math.max(0, screenHeight - windowHeight);
  win.setPosition(posX, posY);

  win.loadFile('index.html');

  // Prevent window closing, minimizing to taskbar instead
  win.on('close', (event) => {
    event.preventDefault();
    win.hide();
  });
}

function toggleWindow() { //  Includes logic for opening and closing window
  if (!win) return;

  if (win.isVisible()) { //If the window is visible, on close it will minimize
    win.hide();
  } else {
    win.show();
    win.focus(); //Shows window and puts into focus on activation
  }
}

function createTray() {
  tray = new Tray(path.join(__dirname, 'placeholder_images', 'temptrayimg.ico'));

  const contextMenu = Menu.buildFromTemplate([ // ✅ FIXED: Corrected Menu reference
    { label: 'Toggle Window', click: toggleWindow }, //Activates togglewindow function
    { type: 'separator' },
    { label: 'Quit', click: () => app.quit() }
  ]);

  tray.setToolTip('Terrarium'); //Title of widget
  tray.setContextMenu(contextMenu);
  tray.on('click', toggleWindow);
}

// ✅ App startup with interactive error handling
app.whenReady()
  .then(() => {
    createWindow();
    createTray();
  })
  .catch(err => {
    console.error('Startup Error:', err.message);

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    rl.question('An error occurred. Do you want to quit the app? (y/n): ', (answer) => {
      if (answer.trim().toLowerCase() === 'y') {
        console.log('Exiting...');
        app.quit();
      } else {
        console.log('Continuing without quitting...');
        rl.close();
      }
    });
  });

//Keep app running when windows closed
app.on('window-all-closed', (e) => {
  e.preventDefault();
});
