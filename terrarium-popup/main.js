//This is the main javascript file for the electron stuff
//It includes the positioning of the window, the scaling,
//And activating the HTML files through index.html

const { app, BrowserWindow, Tray, Menu, screen } = require('electron');
const path = require('path');
const readline = require('readline');

//  Load config
const config = require('./config.json');
//  Global Variables
global.DEVMODE = config.devMode; 

let win;
let tray;

function createWindow() {
  const display = screen.getPrimaryDisplay();
  const { width: screenWidth, height: screenHeight } = display.workAreaSize;

  const widthPercent = config.window.widthPercent;
  const heightPercent = config.window.heightPercent;

  const windowWidth = Math.floor(screenWidth * widthPercent);
  const windowHeight = Math.floor(screenHeight * heightPercent);

  const posX = Math.max(0, screenWidth - windowWidth);
  const posY = Math.max(0, screenHeight - windowHeight);

  win = new BrowserWindow({
    width: windowWidth,
    height: windowHeight,
    x: posX,
    y: posY,
    frame: false,
    transparent: false,
    alwaysOnTop: true,
    resizable: false,
    skipTaskbar: true,
    show: !config.startMinimized, //  Show window based on config
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  win.loadFile('index.html');

  win.on('close', (event) => {
    event.preventDefault();
    win.hide();
  });

  if (global.DEVMODE) {
    win.webContents.openDevTools({ mode: 'detach' }); // Optional dev tool auto-open
  }
}

function toggleWindow() {
  if (!win) return;

  if (win.isVisible()) {
    win.hide();
  } else {
    win.show();
    win.focus();
  }
}

function createTray() {
  tray = new Tray(path.join(__dirname, 'placeholder_images', 'temptrayimg.ico'));

  // ✅ Base context menu
  const contextMenuTemplate = [
    { label: 'Toggle Window', click: toggleWindow },
    { type: 'separator' }
  ];

  //  Add dev options if enabled
  if (global.DEVMODE) {
    contextMenuTemplate.push(
      { label: 'Reload', click: () => win.reload() },
      { label: 'Open DevTools', click: () => win.webContents.openDevTools() },
      { type: 'separator' }
    );
  }

  // ✅ Final menu
  contextMenuTemplate.push({ label: 'Quit', click: () => app.quit() });

  const contextMenu = Menu.buildFromTemplate(contextMenuTemplate);

  tray.setToolTip('Terrarium');
  tray.setContextMenu(contextMenu);
  tray.on('click', toggleWindow);
}

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

app.on('window-all-closed', (e) => {
  e.preventDefault();
});
