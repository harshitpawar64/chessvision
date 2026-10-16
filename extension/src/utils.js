export function makeBoardFen(pieces) {
  const ranks = [];
  for (let r = 7; r >= 0; r--) {
    let rankStr = "";
    let empty = 0;
    const rOffset = r << 3;
    for (let f = 0; f < 8; f++) {
      const p = pieces[rOffset | f];
      if (p === ".") {
        empty++;
      } else {
        if (empty > 0) {
          rankStr += empty;
          empty = 0;
        }
        rankStr += p;
      }
    }
    if (empty > 0) rankStr += empty;
    ranks.push(rankStr);
  }
  return ranks.join("/");
}

export function inferCastling(pieces) {
  let rights = "";
  if (pieces[4] === "K") {
    if (pieces[7] === "R") rights += "K";
    if (pieces[0] === "R") rights += "Q";
  }
  if (pieces[60] === "k") {
    if (pieces[63] === "r") rights += "k";
    if (pieces[56] === "r") rights += "q";
  }
  return rights || "-";
}

export function inferTurn(pieces, orientation) {
  const whiteInCheck = isCheck(pieces, "white");
  const blackInCheck = isCheck(pieces, "black");

  if (whiteInCheck && !blackInCheck) return "white";
  if (blackInCheck && !whiteInCheck) return "black";

  return orientation;
}

const KNIGHT_MOVES = [
  [-2, -1], [-2, 1], [-1, -2], [-1, 2],
  [1, -2], [1, 2], [2, -1], [2, 1],
];
const STRAIGHT_DIRS = [[1, 0], [-1, 0], [0, 1], [0, -1]];
const DIAG_DIRS = [[1, 1], [1, -1], [-1, 1], [-1, -1]];

function isCheck(pieces, color) {
  const kingPiece = color === "white" ? "K" : "k";
  let kingSq = -1;
  for (let s = 0; s < 64; s++) {
    if (pieces[s] === kingPiece) {
      kingSq = s;
      break;
    }
  }
  if (kingSq === -1) return false;

  const kr = kingSq >> 3;
  const kf = kingSq & 7;

  // 1. Knight attacks
  const enemyKnight = color === "white" ? "n" : "N";
  for (const [dr, df] of KNIGHT_MOVES) {
    const r = kr + dr;
    const f = kf + df;
    if (r >= 0 && r < 8 && f >= 0 && f < 8) {
      if (pieces[(r << 3) | f] === enemyKnight) return true;
    }
  }

  // 2. Pawn attacks
  const enemyPawn = color === "white" ? "p" : "P";
  const pawnDir = color === "white" ? 1 : -1;
  const pr = kr + pawnDir;
  if (pr >= 0 && pr < 8) {
    if (kf > 0 && pieces[(pr << 3) | (kf - 1)] === enemyPawn) return true;
    if (kf < 7 && pieces[(pr << 3) | (kf + 1)] === enemyPawn) return true;
  }

  // 3. Adjacent King
  const enemyKing = color === "white" ? "k" : "K";
  for (let dr = -1; dr <= 1; dr++) {
    for (let df = -1; df <= 1; df++) {
      if (dr === 0 && df === 0) continue;
      const r = kr + dr;
      const f = kf + df;
      if (r >= 0 && r < 8 && f >= 0 && f < 8) {
        if (pieces[(r << 3) | f] === enemyKing) return true;
      }
    }
  }

  // 4. Straight sliding attacks (Rook, Queen)
  const enemyRook = color === "white" ? "r" : "R";
  const enemyQueen = color === "white" ? "q" : "Q";
  for (const [dr, df] of STRAIGHT_DIRS) {
    let r = kr + dr;
    let f = kf + df;
    while (r >= 0 && r < 8 && f >= 0 && f < 8) {
      const p = pieces[(r << 3) | f];
      if (p !== ".") {
        if (p === enemyRook || p === enemyQueen) return true;
        break;
      }
      r += dr;
      f += df;
    }
  }

  // 5. Diagonal sliding attacks (Bishop, Queen)
  const enemyBishop = color === "white" ? "b" : "B";
  for (const [dr, df] of DIAG_DIRS) {
    let r = kr + dr;
    let f = kf + df;
    while (r >= 0 && r < 8 && f >= 0 && f < 8) {
      const p = pieces[(r << 3) | f];
      if (p !== ".") {
        if (p === enemyBishop || p === enemyQueen) return true;
        break;
      }
      r += dr;
      f += df;
    }
  }

  return false;
}
