import OpenAI from "openai";
import { format } from "fast-csv";
import { writeFile, existsSync, mkdirSync, createWriteStream } from "fs";

const openai = new OpenAI({
  apiKey: process.env.OPEN_AI_KEY,
});

const numStories = 10; // Number of stories to generate
const storiesDir = "./books"; // Directory to store the stories
const csvFilename = "stories_with_covers.csv"; // CSV filename

// Create stories directory if it doesn't exist
if (!existsSync(storiesDir)) {
  mkdirSync(storiesDir);
}

// Define the universe and characters with detailed descriptions
const universe = "Magical Forest of Eldoria";
const characters = {
  "Fluffy the Wise Owl": {
    description:
      "An ancient owl with silver feathers and wise, glowing eyes. Known for her knowledge of the forest's secrets and sage advice.",
    role: "Guardian of Eldoria's wisdom and guide to the lost.",
  },
  "Milo the Brave Squirrel": {
    description:
      "A small but brave red squirrel, always ready for adventure with his tiny backpack and a keen sense of curiosity.",
    role: "The daring explorer of Eldoria, always on the lookout for new discoveries and adventures.",
  },
  "Luna the Mysterious Fox": {
    description:
      "A sleek, silver fox with enigmatic blue eyes, moving silently through the shadows of the forest.",
    role: "The mysterious wanderer with a knack for uncovering hidden truths and secrets.",
  },
  "Zara the Kind Unicorn": {
    description:
      "A majestic unicorn with a shimmering white coat and a horn that glows under the moonlight, spreading kindness wherever she goes.",
    role: "The gentle soul who brings harmony and heals wounds of the heart and spirit.",
  },
  "Rex the Jolly Dragon": {
    description:
      "A small, emerald-green dragon with a friendly smile, always ready to lend a helping claw and share his wisdom.",
    role: "The keeper of ancient magic and protector of the mystical elements of Eldoria.",
  },
  "Bella the Gentle Butterfly": {
    description:
      "A radiant butterfly with delicate, colorful wings that leave a trail of sparkling dust, symbolizing transformation and hope.",
    role: "The messenger of change, spreading beauty and joy across the forest.",
  },
  "Leo the Curious Rabbit": {
    description:
      "A fluffy, energetic rabbit with the softest fur and the brightest eyes, always hopping around and exploring.",
    role: "The spirited adventurer, always curious and eager to make new friends.",
  },
  "Piper the Playful Fairy": {
    description:
      "A tiny, mischievous fairy with iridescent wings, bringing laughter and fun to all the forest dwellers.",
    role: "The spreader of joy and playfulness, lighting up the forest with her magic.",
  },
  "Oliver the Thoughtful Deer": {
    description:
      "A noble deer with impressive antlers, carrying himself with elegance and poise, always thoughtful and considerate.",
    role: "The wise counselor of Eldoria, offering guidance and support to those in need.",
  },
  "Gemma the Cheerful Gnome": {
    description:
      "A jovial gnome with a red hat and a friendly grin, known for her inventive gadgets and love for gardening.",
    role: "The ingenious inventor and caretaker of the forest's flora.",
  },
  "Chole the Caterpillar": {
    description:
      "A colorful caterpillar with a curious nature, always seen munching on Eldoria's magical leaves and dreaming of flight.",
    role: "The ever-transforming soul, symbolizing growth and change in the journey of life.",
  },
};
// Convert character object keys to an array
const characterNames = Object.keys(characters);

// Function to save a story and cover in a folder
function saveStoryAndCover(storyTitle, storyContent, coverDescription) {
  // Remove 'Title: ' prefix if it exists
  const cleanedTitle = storyTitle.replace(/^Title: /, "");
  const safeTitle = cleanedTitle.replace(/[^a-z0-9]/gi, "_").toLowerCase();
  const storyFolderPath = `${storiesDir}/${safeTitle}`;

  if (!existsSync(storyFolderPath)) {
    mkdirSync(storyFolderPath);
  }

  writeFile(`${storyFolderPath}/${safeTitle}.txt`, storyContent, (err) => {
    if (err) console.error(`Error writing story to file: ${err}`);
  });

  writeFile(`${storyFolderPath}/cover.txt`, coverDescription, (err) => {
    if (err) console.error(`Error writing cover to file: ${err}`);
  });

  console.log(`Saved story and cover for '${cleanedTitle}'`);
}
// Function to save stories and covers to CSV
function saveToCSV(entries) {
  const ws = createWriteStream(csvFilename);
  const csvStream = format({ headers: true });
  csvStream
    .pipe(ws)
    .on("end", () => console.log(`CSV file saved as ${csvFilename}`));

  entries.forEach(({ story, coverDescription }) => {
    const [title, ...contents] = story.split("\n");
    csvStream.write({
      title,
      contents: contents.join("\n"),
      coverDescription,
    });
  });

  csvStream.end();
}

// Function to generate a story and cover description
async function generateStory(characterName) {
  const character = characters[characterName];
  if (!character) {
    console.error(`Character not found: ${characterName}`);
    return;
  }

  try {
    // Enhanced prompt for bedtime story structure
    const storyPrompt = `
            Create a bedtime story in the style of classical fairy tales set in the ${universe}, featuring ${characterName}, ${character.description}. 
            1. Begin with a calm and imaginative setting.
            2. Introduce the character and a simple problem or challenge.
            3. Describe a gentle journey or adventure to overcome the problem.
            4. Resolve the problem with a positive outcome and a moral lesson.
            5. End the story on a soothing note, suitable for bedtime.
            6. Start each page with 'Page 1:'
            7. Add the title of the book at the top with a prefix of Title:
            8. The story should be suitable for an 8-page book, with 1-2 sentences per page. The story should start with the title of the book and reflect the character's role as ${character.role}.
        `.trim();

    const storyResponse = await openai.chat.completions.create({
      messages: [
        {
          role: "system",
          content: storyPrompt,
        },
      ],
      model: "gpt-4-1106-preview",
      max_tokens: 450,
      temperature: 0.7,
    });
    const story = storyResponse.choices[0].message.content.trim();

    // Generate cover image description
    const coverPrompt = `Write a stable diffusion prompt to describe the background (no people or animals) for for the kids story titled: '${
      story.split("\n")[0]
    }', set in the ${universe}. Respond with the prompt only.`;
    const coverResponse = await openai.chat.completions.create({
      messages: [
        {
          role: "system",
          content: coverPrompt,
        },
      ],
      model: "gpt-4-1106-preview",
      max_tokens: 100,
      temperature: 0.7,
    });
    const coverDescription = coverResponse.choices[0].message.content.trim();

    return { story, coverDescription };
  } catch (error) {
    console.error("Error generating story and cover:", error);
  }
}
// Generate multiple stories, save to CSV and process for TTS
async function generateMultipleStories() {
  const entries = [];

  for (let i = 0; i < numStories; i++) {
    const characterName = characterNames[i % characterNames.length];
    if (!characterName) return;
    const { story, coverDescription } = await generateStory(characterName);
    if (story && coverDescription) {
      const [title, ...contents] = story.split("\n");
      const storyContent = contents.join("\n");
      entries.push({ title, contents: storyContent, coverDescription });

      saveStoryAndCover(title, storyContent, coverDescription);
    }
  }

  saveToCSV(entries);
}

generateMultipleStories();
