const { Telegraf } = require('telegraf');
const bot = require('../index');

module.exports = async (req, res) => {
  try {
    await bot.handleUpdate(req.body, res);
  } catch (err) {
    console.error(err);
    res.status(400).send('Error');
  }
};