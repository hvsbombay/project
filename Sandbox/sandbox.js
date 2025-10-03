document.addEventListener('DOMContentLoaded', () => {
    // Matter.js modules
    const { Engine, Render, Runner, World, Bodies, Mouse, MouseConstraint, Composite } = Matter;

    const container = document.getElementById('sandbox-container');
    let canvasWidth = container.clientWidth;
    let canvasHeight = container.clientHeight;

    // Create engine
    const engine = Engine.create();
    const world = engine.world;
    world.gravity.y = 1; // Standard gravity

    // Create renderer
    const render = Render.create({
        element: container,
        engine: engine,
        options: {
            width: canvasWidth,
            height: canvasHeight,
            wireframes: false, // Render shapes with fill colors
            background: '#1f2937' // A slightly lighter dark for the canvas
        }
    });

    Render.run(render);

    // Create runner
    const runner = Runner.create();
    Runner.run(runner, engine);

    // Function to get a random color
    const getRandomColor = () => {
        const randomColor = '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0');
        return randomColor;
    };

    // Add boundary walls
    const wallOptions = { isStatic: true, render: { fillStyle: '#4b5563' } }; // Gray walls
    const wallThickness = 50;
    World.add(world, [
        // Ground
        Bodies.rectangle(canvasWidth / 2, canvasHeight + wallThickness / 2, canvasWidth, wallThickness, wallOptions),
        // Ceiling
        Bodies.rectangle(canvasWidth / 2, -wallThickness / 2, canvasWidth, wallThickness, wallOptions),
        // Left Wall
        Bodies.rectangle(-wallThickness / 2, canvasHeight / 2, wallThickness, canvasHeight, wallOptions),
        // Right Wall
        Bodies.rectangle(canvasWidth + wallThickness / 2, canvasHeight / 2, wallThickness, canvasHeight, wallOptions)
    ]);
    
    // Add mouse control for dragging objects
    const mouse = Mouse.create(render.canvas);
    const mouseConstraint = MouseConstraint.create(engine, {
        mouse: mouse,
        constraint: {
            stiffness: 0.2,
            render: {
                visible: false // Don't show the constraint line
            }
        }
    });

    World.add(world, mouseConstraint);
    // Keep the mouse in sync with rendering
    render.mouse = mouse;

    // --- UI Event Listeners ---

    document.getElementById('add-circle').addEventListener('click', () => {
        const x = Math.random() * (canvasWidth - 80) + 40;
        const radius = Math.random() * 20 + 20;
        const circle = Bodies.circle(x, 50, radius, {
            restitution: 0.7,
            render: { fillStyle: getRandomColor() }
        });
        World.add(world, circle);
    });

    document.getElementById('add-box').addEventListener('click', () => {
        const x = Math.random() * (canvasWidth - 80) + 40;
        const size = Math.random() * 40 + 30;
        const box = Bodies.rectangle(x, 50, size, size, {
            restitution: 0.5,
            render: { fillStyle: getRandomColor() }
        });
        World.add(world, box);
    });
    
    document.getElementById('add-rect').addEventListener('click', () => {
        const x = Math.random() * (canvasWidth - 100) + 50;
        const width = Math.random() * 80 + 40;
        const height = Math.random() * 40 + 30;
        const rect = Bodies.rectangle(x, 50, width, height, {
            restitution: 0.5,
            render: { fillStyle: getRandomColor() }
        });
        World.add(world, rect);
    });


    document.getElementById('add-triangle').addEventListener('click', () => {
       const x = Math.random() * (canvasWidth - 80) + 40;
       const size = Math.random() * 40 + 30;
       const polygon = Bodies.polygon(x, 50, 3, size, {
            restitution: 0.5,
            render: { fillStyle: getRandomColor() }
        });
        World.add(world, polygon);
    });

    document.getElementById('add-pentagon').addEventListener('click', () => {
       const x = Math.random() * (canvasWidth - 80) + 40;
       const size = Math.random() * 40 + 30;
       const polygon = Bodies.polygon(x, 50, 5, size, {
            restitution: 0.5,
            render: { fillStyle: getRandomColor() }
        });
        World.add(world, polygon);
    });

    document.getElementById('clear-btn').addEventListener('click', () => {
        // Remove all non-static bodies from the world
        const allBodies = Composite.allBodies(world);
        allBodies.forEach(body => {
            if (!body.isStatic) {
                World.remove(world, body);
            }
        });
    }); 

    
    
    // Handle window resizing
    const handleResize = () => {
        canvasWidth = container.clientWidth;
        canvasHeight = container.clientHeight;
        
        // Update renderer and canvas
        render.canvas.width = canvasWidth;
        render.canvas.height = canvasHeight;
        render.options.width = canvasWidth;
        render.options.height = canvasHeight;
        
        // Update walls based on new dimensions (remove old ones first)
        const staticBodies = world.bodies.filter(body => body.isStatic);
        World.remove(world, staticBodies);
        
        World.add(world, [
            Bodies.rectangle(canvasWidth / 2, canvasHeight + wallThickness / 2, canvasWidth, wallThickness, wallOptions),
            Bodies.rectangle(canvasWidth / 2, -wallThickness / 2, canvasWidth, wallThickness, wallOptions),
            Bodies.rectangle(-wallThickness / 2, canvasHeight / 2, wallThickness, canvasHeight, wallOptions),
            Bodies.rectangle(canvasWidth + wallThickness / 2, canvasHeight / 2, wallThickness, canvasHeight, wallOptions)
        ]);
    };

    window.addEventListener('resize', handleResize);
    
    // Initial setup for size
    handleResize();
});
