//This is the main javascript file for the electron stuff
//It includes the positioning of the window, the scaling,
//as well as activating the HTML files through index.html

const {app, BrowserWindow, Tray, Menu, screen} = require('electron');
const path = require('path')
const readline = require('readline');
let win;
let tray;

function createWindow() {
  const display = screen.getPrimaryDisplay();
  const { width: screenWidth, height: screenHeight } = display.workAreaSize;

  const widthpercent = 0.20;  //VAR - 15% width
  const heightpercent = 0.40; //VAR - 20% height

  const windowWidth = Math.floor(screenWidth * widthpercent);
  const windowHeight = Math.floor(screenHeight * heightpercent);

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
    show: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  win.loadFile('index.html');

  win.once('ready-to-show', () => {
    win.setBounds({ x: posX, y: posY, width: windowWidth, height: windowHeight });
  });

  win.on('close', (event) => {
    event.preventDefault();
    win.hide();
  });
}
function toggleWindow() {//If the window is visible, on close it will minimize
  if (!win) return;

  if (win.isVisible()) {
    win.hide();
  } else {
    win.show();
    win.focus(); //Shows window and puts into focus on activation
  }
}

function createTray() {
  tray = new Tray(path.join(__dirname, 'placeholder_images', 'temptrayimg.ico'));

  const contextMenu = Menu.buildFromTemplate([ //Fixed menu references, ask before messing with
    {label: 'Toggle Window', click: toggleWindow }, //Activates togglewindow function
    {type: 'separator'},
    {label: 'quit', click: () => app.quit() }
  ]);
  tray.setToolTip('Terrarium'); //Widget Title
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

    //prompting user
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    rl.question('An error occurred. Do you want to exit? (y/n): ', (answer) => {
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

